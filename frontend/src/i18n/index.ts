import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import common_zh_TW from './locales/zh-TW/common.json'
import home_zh_TW from './locales/zh-TW/home.json'
import notebook_zh_TW from './locales/zh-TW/notebook.json'
import chat_zh_TW from './locales/zh-TW/chat.json'
import source_zh_TW from './locales/zh-TW/source.json'
import studio_zh_TW from './locales/zh-TW/studio.json'
import settings_zh_TW from './locales/zh-TW/settings.json'

import common_zh_CN from './locales/zh-CN/common.json'
import home_zh_CN from './locales/zh-CN/home.json'
import notebook_zh_CN from './locales/zh-CN/notebook.json'
import chat_zh_CN from './locales/zh-CN/chat.json'
import source_zh_CN from './locales/zh-CN/source.json'
import studio_zh_CN from './locales/zh-CN/studio.json'
import settings_zh_CN from './locales/zh-CN/settings.json'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      'zh-TW': {
        common: common_zh_TW,
        home: home_zh_TW,
        notebook: notebook_zh_TW,
        chat: chat_zh_TW,
        source: source_zh_TW,
        studio: studio_zh_TW,
        settings: settings_zh_TW,
      },
      'zh-CN': {
        common: common_zh_CN,
        home: home_zh_CN,
        notebook: notebook_zh_CN,
        chat: chat_zh_CN,
        source: source_zh_CN,
        studio: studio_zh_CN,
        settings: settings_zh_CN,
      },
    },
    fallbackLng: 'zh-TW',
    defaultNS: 'common',
    ns: ['common', 'home', 'notebook', 'chat', 'source', 'studio', 'settings'],
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
    },
  })

// 同步更新 HTML lang 属性
i18n.on('languageChanged', (lng: string) => {
  document.documentElement.lang = lng
})

export default i18n
