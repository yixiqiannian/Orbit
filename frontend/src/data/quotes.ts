// 每日一言内置名言库
// 按日期索引取一条（dayOfYear % quotes.length），每天固定一条，离线可用
export interface Quote {
  text: string
  from: string
}

export const quotes: Quote[] = [
  { text: 'Stay hungry, stay foolish.', from: 'Steve Jobs' },
  { text: '路漫漫其修远兮，吾将上下而求索。', from: '屈原《离骚》' },
  { text: 'The only way to do great work is to love what you do.', from: 'Steve Jobs' },
  { text: '不积跬步，无以至千里；不积小流，无以成江海。', from: '荀子《劝学》' },
  { text: 'Simplicity is the ultimate sophistication.', from: 'Leonardo da Vinci' },
  { text: '博观而约取，厚积而薄发。', from: '苏轼' },
  { text: 'Success is not final, failure is not fatal: it is the courage to continue that counts.', from: 'Winston Churchill' },
  { text: '学而不思则罔，思而不学则殆。', from: '孔子《论语》' },
  { text: 'Talk is cheap. Show me the code.', from: 'Linus Torvalds' },
  { text: '纸上得来终觉浅，绝知此事要躬行。', from: '陆游《冬夜读书示子聿》' },
  { text: 'The best time to plant a tree was 20 years ago. The second best time is now.', from: 'Chinese Proverb' },
  { text: '三人行，必有我师焉。择其善者而从之，其不善者而改之。', from: '孔子《论语》' },
  { text: 'Any sufficiently advanced technology is indistinguishable from magic.', from: 'Arthur C. Clarke' },
  { text: '天行健，君子以自强不息；地势坤，君子以厚德载物。', from: '《周易》' },
  { text: 'First, solve the problem. Then, write the code.', from: 'John Johnson' },
  { text: '锲而不舍，金石可镂。', from: '荀子《劝学》' },
  { text: 'The journey of a thousand miles begins with a single step.', from: 'Lao Tzu' },
  { text: '知之者不如好之者，好之者不如乐之者。', from: '孔子《论语》' },
  { text: 'Premature optimization is the root of all evil.', from: 'Donald Knuth' },
  { text: '业精于勤，荒于嬉；行成于思，毁于随。', from: '韩愈《进学解》' },
  { text: 'It does not matter how slowly you go as long as you do not stop.', from: 'Confucius' },
  { text: '千里之行，始于足下。', from: '老子《道德经》' },
  { text: 'Make it work, make it right, make it fast.', from: 'Kent Beck' },
  { text: '工欲善其事，必先利其器。', from: '孔子《论语》' },
  { text: 'Innovation distinguishes between a leader and a follower.', from: 'Steve Jobs' },
  { text: '非淡泊无以明志，非宁静无以致远。', from: '诸葛亮《诫子书》' },
  { text: 'The most dangerous phrase in the language is: We have always done it this way.', from: 'Grace Hopper' },
  { text: '少壮不努力，老大徒伤悲。', from: '《长歌行》' },
  { text: 'Programs must be written for people to read, and only incidentally for machines to execute.', from: 'Harold Abelson' },
  { text: '志不强者智不达，言不信者行不果。', from: '墨子' },
  { text: 'The purpose of our lives is to be happy.', from: 'Dalai Lama' },
  { text: '书山有路勤为径，学海无涯苦作舟。', from: '韩愈' },
  { text: 'Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.', from: 'Antoine de Saint-Exupéry' },
  { text: '凡事预则立，不预则废。', from: '《礼记·中庸》' },
  { text: 'The best way to predict the future is to invent it.', from: 'Alan Kay' },
  { text: '海纳百川，有容乃大；壁立千仞，无欲则刚。', from: '林则徐' },
  { text: 'Quality is not an act, it is a habit.', from: 'Aristotle' },
  { text: '温故而知新，可以为师矣。', from: '孔子《论语》' },
  { text: 'There are only two hard things in computer science: cache invalidation and naming things.', from: 'Phil Karlton' },
  { text: '穷则独善其身，达则兼济天下。', from: '孟子' },
  { text: 'Live as if you were to die tomorrow. Learn as if you were to live forever.', from: 'Mahatma Gandhi' },
  { text: '业精于勤，而荒于嬉。', from: '韩愈' },
  { text: 'Software is a great combination between artistry and engineering.', from: 'Bill Gates' },
  { text: '知人者智，自知者明。胜人者有力，自胜者强。', from: '老子《道德经》' },
  { text: 'In the middle of difficulty lies opportunity.', from: 'Albert Einstein' },
  { text: '宝剑锋从磨砺出，梅花香自苦寒来。', from: '《警世贤文》' },
  { text: 'The secret of getting ahead is getting started.', from: 'Mark Twain' },
  { text: '问渠那得清如许？为有源头活水来。', from: '朱熹《观书有感》' },
  { text: 'Code is like humor. When you have to explain it, it is bad.', from: 'Cory House' },
  { text: '勿以恶小而为之，勿以善小而不为。', from: '刘备' },
  { text: 'Whether you think you can or you think you can not, you are right.', from: 'Henry Ford' },
  { text: '玉不琢，不成器；人不学，不知道。', from: '《礼记·学记》' },
  { text: 'The best error message is the one that never shows up.', from: 'Thomas Fuchs' },
  { text: '人无远虑，必有近忧。', from: '孔子《论语》' },
  { text: 'Do what you can, with what you have, where you are.', from: 'Theodore Roosevelt' },
  { text: '黑发不知勤学早，白首方悔读书迟。', from: '颜真卿《劝学》' },
  { text: 'Simplicity is prerequisite for reliability.', from: 'Edsger W. Dijkstra' },
  { text: '君子和而不同，小人同而不和。', from: '孔子《论语》' },
  { text: 'The future belongs to those who believe in the beauty of their dreams.', from: 'Eleanor Roosevelt' },
  { text: '读书破万卷，下笔如有神。', from: '杜甫' },
  { text: 'Measurement is the first step that leads to control and eventually to improvement.', from: 'H. James Harrington' },
  { text: '满招损，谦受益。', from: '《尚书》' },
  { text: 'Great things are done by a series of small things brought together.', from: 'Vincent Van Gogh' },
  { text: '会当凌绝顶，一览众山小。', from: '杜甫《望岳》' },
  { text: 'Debugging is twice as hard as writing the code in the first place.', from: 'Brian Kernighan' },
  { text: '静以修身，俭以养德。', from: '诸葛亮《诫子书》' },
  { text: 'The impediment to action advances action. What stands in the way becomes the way.', from: 'Marcus Aurelius' },
  { text: '敏而好学，不耻下问。', from: '孔子《论语》' },
  { text: 'Happiness is not something ready-made. It comes from your own actions.', from: 'Dalai Lama' },
  { text: '不飞则已，一飞冲天；不鸣则已，一鸣惊人。', from: '司马迁《史记》' }
]

/** 按当天日期取一条，保证每天固定 */
export function getDailyQuote(): Quote {
  const now = new Date()
  const start = new Date(now.getFullYear(), 0, 0)
  const dayOfYear = Math.floor((now.getTime() - start.getTime()) / 86400000)
  return quotes[dayOfYear % quotes.length]
}
