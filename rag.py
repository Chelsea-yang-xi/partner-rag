def load_chunks(path):
    text = open(path, encoding="utf-8").read()   # encoding 参数防止 Windows 中文系统读文件乱码,open() 返回文件对象，.read() 一口气读成一个大字符串。 
    chunks = []
    for part in text.split("## "):
        if part.strip() != "":
            chunks.append(part.strip())
    return chunks

chunks = load_chunks("handbook.md")   # 相对路径:因为俩文件在同一个文件夹
print("共载入", len(chunks), "个chunk")

def score_chunk(question_words, chunk):
    chunk_lower = chunk.lower()
    score = 0
    for word in question_words:
        if word in chunk_lower:
            score += 1
    return score


def get_keywords(question):
    words = []
    for w in question.replace("?", "").replace(",", "").lower().split():
        if len(w) > 3:
            words.append(w)
    return words


def retrieve(question, chunks):
    question_words = get_keywords(question)      # 获取问题中的关键词
    best_chunk = None
    best_score = 0
    for chunk in chunks:                        # 给每个chunk打分,打擂台
        s = score_chunk(question_words, chunk)
        if s > best_score:
            best_score = s
            best_chunk = chunk
    return best_chunk, best_score, len(question_words)


def build_prompt(question, chunk):
    return f"""You are a partner support assistant for account managers.
Answer ONLY based on the material below.
If the material does not contain the answer, reply exactly: "Not found in handbook."
Always mention which section your answer comes from.

MATERIAL:
{chunk}

QUESTION: {question}

ANSWER:"""


def answer(question, chunks):
    chunk, score, total = retrieve(question, chunks)
    if chunk is None or score == 0:                 # 护栏: 什么都没检索到
        return "Not found in handbook."  # 抽取式回答: 从命中chunk里挑出含问题关键词的句子
    question_words = get_keywords(question)
    title = chunk.split("\n")[0]                    # 章节标题(做出处引用)
    sentences = chunk.replace("\n", " ").split(". ")  # 按句号切成句子
    picked = []
    for s in sentences:
        if score_chunk(question_words, s) > 0:      # 复用你的打分函数!
            picked.append(s.strip())
    if len(picked) == 0:
        return "Not found in handbook."
    return ". ".join(picked) + ". (Source: " + title + ")"


# rag.py 底部,原来的执行代码全部缩进包进这个 if 里:
if __name__ == "__main__":
    chunks = load_chunks("handbook.md")
    for q in ["How much rebate do I get?",
              "What is the warranty for robotic vacuum?",
              "What time should I go to sleep?",
              "How much time do I have to report delivery problems?"]:
        print("Q:", q)
        print("A:", answer(q, chunks))
        print()
