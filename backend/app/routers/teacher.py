"""Teacher routes: register, login, classroom CRUD, assignment CRUD.
Also: child-side endpoint to join classroom and list assignments.
"""
import secrets
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.teacher import Teacher
from app.models.classroom import Classroom, ClassroomStudent, Assignment, AssignmentProgress
from app.models.child import Child
from app.models.question import Question
from app.models.device import Device
from app.schemas.teacher import (
    TeacherRegister, TeacherLogin, TeacherOut,
    ClassroomCreate, ClassroomOut,
    AssignmentCreate, AssignmentOut,
)
from app.routers.deps import get_current_parent, get_child_from_device_token
from app.services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/teacher", tags=["teacher"])


# ─── Teacher Auth ───

@router.post("/register", status_code=201)
def teacher_register(req: TeacherRegister, db: Session = Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(400, "密碼至少 6 字符")
    existing = db.query(Teacher).filter(Teacher.email == req.email).first()
    if existing:
        raise HTTPException(400, "此 Email 已註冊")
    teacher = Teacher(
        email=req.email,
        password_hash=hash_password(req.password),
        name=req.name,
        school=req.school,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    token = create_access_token({"sub": teacher.id, "role": "teacher"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "teacher": TeacherOut.model_validate(teacher).model_dump(),
    }


@router.post("/login")
def teacher_login(req: TeacherLogin, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.email == req.email).first()
    if not teacher or not verify_password(req.password, teacher.password_hash):
        raise HTTPException(401, "郵箱或密碼錯誤")
    token = create_access_token({"sub": teacher.id, "role": "teacher"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "teacher": TeacherOut.model_validate(teacher).model_dump(),
    }


# ─── Get current teacher from JWT ───

from app.services.auth_service import decode_access_token


def get_current_teacher(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> Teacher:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "未登入")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "teacher":
        raise HTTPException(401, "教師憑證無效")
    teacher = db.query(Teacher).filter(Teacher.id == payload["sub"]).first()
    if not teacher:
        raise HTTPException(401, "教師不存在")
    return teacher


# ─── Classroom CRUD ───
def _gen_invite_code() -> str:
    return secrets.token_hex(3).upper()  # 6 chars


@router.post("/classrooms", response_model=ClassroomOut, status_code=201)
def create_classroom(
    req: ClassroomCreate,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    code = _gen_invite_code()
    while db.query(Classroom).filter(Classroom.invite_code == code).first():
        code = _gen_invite_code()

    cr = Classroom(
        teacher_id=teacher.id, name=req.name,
        grade=req.grade, subject=req.subject,
        invite_code=code,
    )
    db.add(cr)
    db.commit()
    db.refresh(cr)
    return ClassroomOut(
        id=cr.id, teacher_id=cr.teacher_id, name=cr.name,
        grade=cr.grade, subject=cr.subject, invite_code=cr.invite_code,
        student_count=0, assignment_count=0, created_at=cr.created_at,
    )


@router.get("/classrooms", response_model=list[ClassroomOut])
def list_classrooms(
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    crs = db.query(Classroom).filter(Classroom.teacher_id == teacher.id).all()
    result = []
    for cr in crs:
        sc = db.query(ClassroomStudent).filter(ClassroomStudent.classroom_id == cr.id).count()
        ac = db.query(Assignment).filter(Assignment.classroom_id == cr.id).count()
        result.append(ClassroomOut(
            id=cr.id, teacher_id=cr.teacher_id, name=cr.name,
            grade=cr.grade, subject=cr.subject, invite_code=cr.invite_code,
            student_count=sc, assignment_count=ac, created_at=cr.created_at,
        ))
    return result


@router.delete("/classrooms/{classroom_id}")
def delete_classroom(
    classroom_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    cr = db.query(Classroom).filter(Classroom.id == classroom_id, Classroom.teacher_id == teacher.id).first()
    if not cr:
        raise HTTPException(404, "班級不存在")
    db.delete(cr)
    db.commit()
    return {"message": "班級已刪除"}


# ─── Assignment CRUD ───

@router.post("/assignments", response_model=AssignmentOut, status_code=201)
def create_assignment(
    req: AssignmentCreate,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    cr = db.query(Classroom).filter(
        Classroom.id == req.classroom_id, Classroom.teacher_id == teacher.id
    ).first()
    if not cr:
        raise HTTPException(404, "班級不存在")

    # Validate questions exist
    for qid in req.question_ids:
        if not db.query(Question).filter(Question.id == qid).first():
            raise HTTPException(400, f"題目 {qid} 不存在")

    a = Assignment(
        classroom_id=req.classroom_id, teacher_id=teacher.id,
        title=req.title, description=req.description,
        question_ids=req.question_ids, due_date=req.due_date,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    total = db.query(ClassroomStudent).filter(ClassroomStudent.classroom_id == cr.id).count()
    return AssignmentOut(
        id=a.id, classroom_id=a.classroom_id, teacher_id=a.teacher_id,
        title=a.title, description=a.description, question_ids=a.question_ids,
        due_date=a.due_date, is_active=a.is_active,
        completed_count=0, total_students=total, created_at=a.created_at,
    )


@router.get("/assignments/{classroom_id}", response_model=list[AssignmentOut])
def list_assignments(
    classroom_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    cr = db.query(Classroom).filter(
        Classroom.id == classroom_id, Classroom.teacher_id == teacher.id
    ).first()
    if not cr:
        raise HTTPException(404, "班級不存在")

    assignments = db.query(Assignment).filter(Assignment.classroom_id == classroom_id).all()
    total_students = db.query(ClassroomStudent).filter(ClassroomStudent.classroom_id == classroom_id).count()
    result = []
    for a in assignments:
        completed = db.query(AssignmentProgress).filter(
            AssignmentProgress.assignment_id == a.id,
            AssignmentProgress.completed_at.isnot(None),
        ).count()
        result.append(AssignmentOut(
            id=a.id, classroom_id=a.classroom_id, teacher_id=a.teacher_id,
            title=a.title, description=a.description, question_ids=a.question_ids,
            due_date=a.due_date, is_active=a.is_active,
            completed_count=completed, total_students=total_students,
            created_at=a.created_at,
        ))
    return result


@router.delete("/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    a = db.query(Assignment).filter(
        Assignment.id == assignment_id, Assignment.teacher_id == teacher.id
    ).first()
    if not a:
        raise HTTPException(404, "作業不存在")
    db.delete(a)
    db.commit()
    return {"message": "作業已刪除"}


# ─── Child-side: join classroom via invite code ───

@router.post("/join")
def join_classroom(
    payload: dict,
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Child joins a classroom using invite code."""
    code = payload.get("invite_code", "").strip().upper()
    cr = db.query(Classroom).filter(Classroom.invite_code == code).first()
    if not cr:
        raise HTTPException(404, "邀請碼無效")

    existing = db.query(ClassroomStudent).filter(
        ClassroomStudent.classroom_id == cr.id,
        ClassroomStudent.child_id == child.id,
    ).first()
    if existing:
        raise HTTPException(400, "已加入此班級")

    cs = ClassroomStudent(classroom_id=cr.id, child_id=child.id)
    db.add(cs)
    db.commit()
    return {"message": f"已加入「{cr.name}」", "classroom_id": cr.id}


# ─── Child-side: list my assignments ───

@router.get("/my-assignments")
def my_assignments(
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """List all assignments for classrooms the child has joined."""
    classrooms = db.query(ClassroomStudent).filter(ClassroomStudent.child_id == child.id).all()
    class_ids = [cs.classroom_id for cs in classrooms]

    if not class_ids:
        return []

    assignments = db.query(Assignment).filter(
        Assignment.classroom_id.in_(class_ids),
        Assignment.is_active == True,
    ).all()

    result = []
    for a in assignments:
        prog = db.query(AssignmentProgress).filter(
            AssignmentProgress.assignment_id == a.id,
            AssignmentProgress.child_id == child.id,
        ).first()

        # Get question details
        questions = db.query(Question).filter(Question.id.in_(a.question_ids)).all()
        q_list = [{"id": q.id, "content": q.content, "type": q.type,
                    "options": q.options, "subject": q.subject, "difficulty": q.difficulty,
                    "tags": q.tags, "avg_time_sec": q.avg_time_sec}
                   for q in questions if q.status == "approved"]

        completed_ids = prog.completed_question_ids if prog else []
        result.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "due_date": a.due_date.isoformat() if a.due_date else None,
            "total_questions": len(q_list),
            "completed_questions": len(completed_ids),
            "completed": prog.completed_at is not None if prog else False,
            "score": prog.score if prog else 0,
            "questions": q_list,
        })

    return result


# ─── Child-side: submit assignment answer ───

class AssignmentAnswerSubmit(BaseModel):
    question_id: int
    selected_answer: str
    time_taken_sec: float = 0.0


@router.post("/assignments/{assignment_id}/answer")
def submit_assignment_answer(
    assignment_id: int,
    question_id: int,
    selected_answer: str,
    time_taken_sec: float = 0.0,
    child: Child = Depends(get_child_from_device_token),
    db: Session = Depends(get_db),
):
    """Submit a single answer within an assignment."""
    a = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not a:
        raise HTTPException(404, "作業不存在")
    if question_id not in a.question_ids:
        raise HTTPException(400, "此題不在作業中")

    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(404, "題目不存在")

    is_correct = selected_answer.strip().lower() == q.answer.strip().lower()
    if q.type == "fill_blank":
        correct_parts = [x.strip().lower() for x in q.answer.split("|")]
        user_parts = [x.strip().lower() for x in selected_answer.split("|")]
        while len(user_parts) < len(correct_parts):
            user_parts.append("")
        is_correct = all(u == c for u, c in zip(user_parts, correct_parts))

    # Update or create progress
    prog = db.query(AssignmentProgress).filter(
        AssignmentProgress.assignment_id == assignment_id,
        AssignmentProgress.child_id == child.id,
    ).first()
    if not prog:
        prog = AssignmentProgress(
            assignment_id=assignment_id, child_id=child.id,
            completed_question_ids=[], score=0, total=len(a.question_ids),
        )
        db.add(prog)

    if question_id not in prog.completed_question_ids:
        prog.completed_question_ids = prog.completed_question_ids + [question_id]
        if is_correct:
            prog.score += 1

    if len(prog.completed_question_ids) >= len(a.question_ids):
        prog.completed_at = datetime.utcnow()

    db.commit()

    return {
        "is_correct": is_correct,
        "correct_answer": q.answer,
        "explanation": q.explanation,
        "completed": prog.completed_at is not None,
        "score": prog.score,
        "total": prog.total,
    }
