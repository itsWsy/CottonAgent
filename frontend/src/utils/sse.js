import { fetchEventSource } from '@microsoft/fetch-event-source'
import { storage } from './storage'

export function connectSse(url, onEvent, options = {}) {
  const controller = new AbortController()
  fetchEventSource(url, {
    signal: controller.signal,
    headers: { Authorization: `Bearer ${storage.getToken()}` },
    openWhenHidden: true,
    async onopen(response) {
      if (!response.ok) throw new Error(`SSE 连接失败：${response.status}`)
      options.onOpen?.()
    },
    onmessage(message) {
      if (message.data) onEvent(JSON.parse(message.data))
    },
    onerror(error) {
      options.onError?.(error)
      return 3000
    },
    onclose() {
      options.onClose?.()
    }
  })
  return () => controller.abort()
}
