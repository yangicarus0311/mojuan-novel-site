import { test } from 'node:test'
import assert from 'node:assert/strict'
import { paginateText, pageForPosition, createReadingClock } from '../src/utils/reading.js'
import { highlightParts } from '../src/utils/highlight.js'

test('pagination preserves every character and fits measured capacity', () => {
  const text = '首段\n\n次段😀 <b>正文</b>  尾段'
  const pages = paginateText(text, value => Array.from(value).length <= 6)
  assert.equal(pages.map(p => p.text).join(''), text)
  assert.ok(pages.every(p => Array.from(p.text).length <= 6))
  assert.equal(pages.at(-1).end, text.length)
})

test('reflow preserves the character position across different capacities', () => {
  const text = '一二三四五六七八九十'.repeat(4)
  const small = paginateText(text, value => value.length <= 5)
  const large = paginateText(text, value => value.length <= 13)
  const offset = small[3].end
  const page = large[pageForPosition(large, offset)]
  assert.ok(page.start <= offset && page.end >= offset)
})

test('empty text and a very small container still terminate', () => {
  assert.equal(paginateText('', () => false).length, 1)
  assert.equal(paginateText('甲乙', () => false).length, 2)
})

test('highlighting keeps HTML and regex metacharacters as literal text', () => {
  const text = '<img src=x onerror=alert(1)> [a] [a]'
  const parts = highlightParts(text, '[a]')
  assert.equal(parts.map(p => p.text).join(''), text)
  assert.equal(parts.filter(p => p.matched).length, 2)
  assert.equal(highlightParts('abc', '')[0].text, 'abc')
})

test('reading clock excludes hidden time and caps suspended gaps', () => {
  let time = 0
  const clock = createReadingClock(() => time)
  time = 1000; clock.tick(true)
  time = 61000; clock.tick(false)
  assert.equal(clock.pending(), 1)
  time = 121000; clock.tick(true)
  assert.equal(clock.pending(), 6)
  clock.acknowledge(6)
  assert.equal(clock.pending(), 0)
})
