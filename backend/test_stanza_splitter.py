# -*- coding: utf-8 -*-
"""
测试 Stanza 分句器效果
"""

from app.utils.sentence_splitter import split_sentences


def test_sentence_splitting():
    """测试各种复杂的中文分句场景"""

    test_cases = [
        {
            "name": "简单句子",
            "text": "这是第一句话。这是第二句话。这是第三句话！"
        },
        {
            "name": "引号内的句子",
            "text": '他说："你好吗？今天天气真好。"我回答说："还不错。"'
        },
        {
            "name": "省略号和感叹号",
            "text": "我真的不知道……但是我觉得……也许可以试试！真的很有趣！"
        },
        {
            "name": "括号和书名号",
            "text": "这本书（《红楼梦》）是中国四大名著之一。你读过吗？"
        },
        {
            "name": "英文缩写",
            "text": "Dr. Smith works at U.S. Department. He has a Ph.D. in Computer Science."
        },
        {
            "name": "混合中英文",
            "text": "我在MIT学习。那里的教授很优秀。你呢？Are you studying too?"
        },
        {
            "name": "复杂标点",
            "text": "哇！真的吗？不可能……这怎么可能？！太惊人了！！！"
        },
        {
            "name": "长文本",
            "text": """人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支。
它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。
可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。"""
        }
    ]

    print("=" * 80)
    print("测试 Stanza 中文分句器")
    print("=" * 80)
    print()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        print("-" * 80)
        print(f"原文:\n{test_case['text']}")
        print()

        # 使用 Stanza 分句
        try:
            sentences = split_sentences(test_case['text'], use_stanza=True)
            print(f"✅ Stanza 分句结果 (共 {len(sentences)} 句):")
            for idx, sent in enumerate(sentences, 1):
                print(f"  [{idx}] {sent}")
        except Exception as e:
            print(f"❌ Stanza 分句失败: {e}")

            # 回退到正则表达式
            sentences_regex = split_sentences(test_case['text'], use_stanza=False)
            print(f"⚠️ 回退到正则表达式分句 (共 {len(sentences_regex)} 句):")
            for idx, sent in enumerate(sentences_regex, 1):
                print(f"  [{idx}] {sent}")

        print()

    print("=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_sentence_splitting()
