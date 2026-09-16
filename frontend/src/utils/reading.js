// Keep plain text intact, including whitespace and surrogate pairs.
export function paginateText(text, fits) {
  const characters = Array.from(text || '')
  const pages = []
  let offset = 0
  let start = 0
  while (start < characters.length) {
    let low = 1
    let high = characters.length - start
    let count = 1
    while (low <= high) {
      const mid = Math.floor((low + high) / 2)
      if (fits(characters.slice(start, start + mid).join(''))) {
        count = mid
        low = mid + 1
      } else high = mid - 1
    }
    const content = characters.slice(start, start + count).join('')
    pages.push({ text: content, start: offset, end: offset + content.length })
    offset += content.length
    start += count
  }
  return pages.length ? pages : [{ text: '', start: 0, end: 0 }]
}

export function pageForPosition(pages, offset) {
  const index = pages.findIndex(page => page.end >= offset)
  return index < 0 ? Math.max(0, pages.length - 1) : index
}

export function createReadingClock(now = () => performance.now()) {
  let previous = now()
  let seconds = 0
  return {
    tick(active) {
      const current = now()
      // Long gaps indicate a suspended device/tab, not continuous reading.
      if (active) seconds = Math.min(60, seconds + Math.max(0, Math.min(5, (current - previous) / 1000)))
      previous = current
    },
    pending() { return Math.floor(seconds) },
    acknowledge(amount) { seconds = Math.max(0, seconds - amount) },
  }
}
