export function highlightParts(text, keyword) {
  text = String(text ?? '')
  keyword = String(keyword ?? '')
  if (!keyword) return [{ text, matched: false }]
  const source = text.toLocaleLowerCase()
  const needle = keyword.toLocaleLowerCase()
  const parts = []
  let offset = 0
  let match
  while ((match = source.indexOf(needle, offset)) !== -1) {
    if (match > offset) parts.push({ text: text.slice(offset, match), matched: false })
    parts.push({ text: text.slice(match, match + keyword.length), matched: true })
    offset = match + keyword.length
  }
  if (offset < text.length) parts.push({ text: text.slice(offset), matched: false })
  return parts
}
