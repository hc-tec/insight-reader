# -*- coding: utf-8 -*-
"""
测试新的句子拆分器
"""

from app.utils.sentence_splitter import split_sentences, split_paragraphs


def test_chinese_sentences():
    """测试中文句子拆分"""
    print("=" * 50)
    print("测试1: 中文句子拆分")
    print("=" * 50)

    text = """人工智能正在改变世界。它让我们的生活更加便捷！但���时也带来了新的挑战？我们应该如何应对…这是一个值得深思的问题。"""

    sentences = split_sentences(text)
    print(f"原文: {text}")
    print(f"\n拆分结果 ({len(sentences)}个句子):")
    for i, sent in enumerate(sentences, 1):
        print(f"{i}. {sent}")


def test_english_sentences():
    """测试英文句子拆分"""
    print("\n" + "=" * 50)
    print("测试2: 英文句子拆分")
    print("=" * 50)

    text = """Dr. Smith works at U.S. Inc. He has a Ph.D. in Computer Science. His research focuses on AI."""

    sentences = split_sentences(text)
    print(f"原文: {text}")
    print(f"\n拆分结果 ({len(sentences)}个句子):")
    for i, sent in enumerate(sentences, 1):
        print(f"{i}. {sent}")


def test_mixed_sentences():
    """测试中英文混合句子拆分"""
    print("\n" + "=" * 50)
    print("测试3: 中英文混合句子拆分")
    print("=" * 50)

    text = """OpenAI发布了GPT-4模型。这个模型在各项测试中表现优异！它可以处理多种语言，包括中文和English. The model shows great potential."""

    sentences = split_sentences(text)
    print(f"原文: {text}")
    print(f"\n拆分结果 ({len(sentences)}个句子):")
    for i, sent in enumerate(sentences, 1):
        print(f"{i}. {sent}")


def test_quotes_and_parentheses():
    """测试引号和括号"""
    print("\n" + "=" * 50)
    print("测试4: 引号和括号处理")
    print("=" * 50)

    text = """他说："人工智能将改变世界。"这是一个大胆的预测。有人认为（包括许多专家）这种说法言过其实。"""

    sentences = split_sentences(text)
    print(f"原文: {text}")
    print(f"\n拆分结果 ({len(sentences)}个句子):")
    for i, sent in enumerate(sentences, 1):
        print(f"{i}. {sent}")


def test_numbers():
    """测试数字处理"""
    print("\n" + "=" * 50)
    print("测试5: 数字和小数点处理")
    print("=" * 50)

    text = """这个算法的准确率达到了98.5%。测试数据集包含10000个样本。每个样本的平均处理时间为0.05秒。"""

    sentences = split_sentences(text)
    print(f"原文: {text}")
    print(f"\n拆分结果 ({len(sentences)}个句子):")
    for i, sent in enumerate(sentences, 1):
        print(f"{i}. {sent}")


def test_paragraphs():
    """测试段落拆分"""
    print("\n" + "=" * 50)
    print("测试6: 段落拆分")
    print("=" * 50)

    text = """人工智能是计算机科学的一个分支。它试图理解智能的实质。

机器学习是人工智能的核心技术之一。通过学习数据中的模式，机器可以做出预测。

深度学习是机器学习的一个子领域。它使用神经网络来模拟人脑的工作方式。"""

    paragraphs = split_paragraphs(text)
    print(f"原文:\n{text}")
    print(f"\n拆分结果 ({len(paragraphs)}个段落):")
    for para in paragraphs:
        print(f"\n段落 {para['index']}:")
        for sent in para['sentences']:
            print(f"  句子 {sent['index']}: {sent['text']}")


def test_ellipsis():
    """测试省略号处理"""
    print("\n" + "=" * 50)
    print("测试7: 省略号处理")
    print("=" * 50)

    text = """这个问题很复杂…我需要时间思考。他说："我不确定…但我会尽力。"最后他成功了！"""

    sentences = split_sentences(text)
    print(f"原文: {text}")
    print(f"\n拆分结果 ({len(sentences)}个句子):")
    for i, sent in enumerate(sentences, 1):
        print(f"{i}. {sent}")


if __name__ == "__main__":
    print("\n[TEST] 开始测试句子拆分器（零依赖，轻量级）\n")

    test_chinese_sentences()
    test_english_sentences()
    test_mixed_sentences()
    test_quotes_and_parentheses()
    test_numbers()
    test_paragraphs()
    test_ellipsis()

    print("\n" + "=" * 50)
    print("[OK] 所有测试完成！")
    print("=" * 50)
