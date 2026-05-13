import { worksAPI, chaptersAPI, bookshelfAPI } from './index'

export const getWorks = (params) => worksAPI.getList(params)
export const getWork = (id) => worksAPI.getById(id)
export const searchWorks = (q) => worksAPI.search(q)
export const getChapter = (id) => chaptersAPI.getById(id)
export const getChapters = (workId) => chaptersAPI.getList(workId)
export const getBookshelf = () => bookshelfAPI.getList()
export const addToBookshelf = (workId) => bookshelfAPI.add(workId)
export const removeFromBookshelf = (workId) => bookshelfAPI.remove(workId)
