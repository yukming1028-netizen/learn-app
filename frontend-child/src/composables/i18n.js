/**
 * i18n composable — lightweight translation without external deps.
 * Usage:
 *   import { useI18n } from '../composables/i18n'
 *   const { t, locale, setLocale } = useI18n()
 *   t('quiz.submit')  // → "提交" or "Submit"
 */
import { ref, computed } from 'vue'
import zhTW from '../i18n/zh-TW.json'
import zhCN from '../i18n/zh-CN.json'
import enUS from '../i18n/en-US.json'

const messages = {
  'zh-TW': zhTW,
  'zh-CN': zhCN,
  'en-US': enUS,
}

const stored = localStorage.getItem('locale') || navigator.language || 'zh-TW'
const locale = ref(messages[stored] ? stored : 'zh-TW')

function getNested(obj, path) {
  return path.split('.').reduce((acc, key) => acc?.[key], obj)
}

export function useI18n() {
  function t(key) {
    const msg = getNested(messages[locale.value], key)
    return msg !== undefined ? msg : getNested(messages['zh-TW'], key) ?? key
  }

  function setLocale(lang) {
    if (messages[lang]) {
      locale.value = lang
      localStorage.setItem('locale', lang)
    }
  }

  const availableLocales = Object.keys(messages)

  return { t, locale, setLocale, availableLocales }
}
