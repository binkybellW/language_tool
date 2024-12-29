import streamlit as st
import re
import jieba
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import pandas as pd

def generate_wordcloud(analysis_text):
    remove_stop_words = st.checkbox('去除停用词', value=False, key='remove_stop_words_checkbox')
    
    custom_stop_words = st.text_area(
        '自定义停用词（使用英文逗号 , 分隔，例如：的,和,etc,and）',
        value='',
        help='请使用英文逗号(,)分隔每个停用词，支持中英文混合输入',
        key='custom_stop_words_textarea'
    )
    
    try:
        # 将文本中的多个空格合并为单个空格
        text = ' '.join(analysis_text.split())
        
        if remove_stop_words:
            # 更新停用词列表
            stop_words = set(word.strip() for word in custom_stop_words.split(',') if word.strip())
            stop_words.update(['我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', 
                               '的', '了', '和', '在', '是', '不', '也', '有', '对', '到', '说', 
                               '看', '很', '都', '这', '那', '什么', '就', '人', '因为', '怎么', 
                               '一个', '而', '但', '会', '能', '让', '如果', '又', '用', '自己', 
                               '多', '没', '为', '去', '然后', '这样', '那样', '真的', '所以', 
                               '其实', '并', '吧', '吗', '呢', '就是', '而且', '或者', '可以', 
                               '可能', '像', '要', '比如', '从', '更', '这儿', '那儿', '那么','等','如此'])
            
            # 分别处理英文和中文
            english_words = [word for word in re.findall(r'[A-Za-z]+', text) if word.lower() not in stop_words]
            
            chinese_text = ''.join(re.findall(r'[\u4e00-\u9fff]+', text))
            chinese_words = [word for word in jieba.lcut(chinese_text) if word not in stop_words]
            
            # 合并中英文词频统计
            all_words = english_words + chinese_words
            word_freq = Counter(all_words)
        else:
            # 不去除连接词的处理
            english_words = re.findall(r'[A-Za-z]+', text)
            chinese_text = ''.join(re.findall(r'[\u4e00-\u9fff]+', text))
            chinese_words = jieba.lcut(chinese_text)
            all_words = english_words + chinese_words
            word_freq = Counter(all_words)
        
        # 创建词云图
        wc = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            max_words=200,
            font_path='./static/Hiragino Sans GB.ttc',  # 使用支持中英文的字体
            random_state=42
        ).generate_from_frequencies(word_freq)
        
        # 显示词云图
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        plt.tight_layout(pad=0)
        
        # 在Streamlit中显示词云图
        st.pyplot(fig)
        
        # 提供下载词云图的选项
        img = io.BytesIO()
        plt.savefig(img, format='pdf')
        img.seek(0)
        
        st.download_button(
            label="下载词云图",
            data=img,
            file_name="wordcloud.pdf",
            mime="application/pdf"  # mime参数指定了文件的MIME类型，这里是PDF文件
        )
        plt.close()
    except Exception as e:
        st.error(f"生成词云图失败: {str(e)}")
        
def count_word_frequency(analysis_text):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        remove_punctuation = st.checkbox('去除标点符号')
    with col2:
        remove_stopwords = st.checkbox('去除停用词')
    with col3:
        remove_numbers = st.checkbox('去除数字')
    with col4:
        top_n = st.number_input('显示前N个词', min_value=1, value=20)
    words = jieba.lcut(analysis_text)
    
    if remove_punctuation:
        words = [w for w in words if not re.match(r'[^\w]', w)]
        
    if remove_stopwords:
        stopwords = ['我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', 
                     '的', '了', '和', '在', '是', '不', '也', '有', '对', '到', '说', 
                     '看', '很', '都', '这', '那', '什么', '就', '人', '因为', '怎么', 
                     '一个', '而', '但', '会', '能', '让', '如果', '又', '用', '自己', 
                     '多', '没', '为', '去', '然后', '这样', '那样', '真的', '所以', 
                     '其实', '并', '吧', '吗', '呢', '就是', '而且', '或者', '可以', 
                     '可能', '像', '要', '比如', '从', '更', '这儿', '那儿', '那么','等','如此']
        words = [w for w in words if w not in stopwords]
    
    if remove_numbers:
        words = [w for w in words if not w.isdigit()]
    
    word_freq = Counter(words)
    freq_df = pd.DataFrame.from_dict(word_freq, orient='index', columns=['频次'])
    freq_df = freq_df.sort_values('频次', ascending=False)
    
    # 只保留前N个
    freq_df = freq_df.head(top_n)
    
    st.write('词频统计结果:')
    st.dataframe(freq_df)
    
    # 导出词频统计结果
    csv = freq_df.to_csv(encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="下载词频统计结果", 
        data=csv,
        file_name="word_frequency.csv",
        mime="text/csv"
    )
    
    
def count_characters(analysis_text):
    # 统计总字数
    char_count = len(analysis_text)
    word_count = len(analysis_text.split())
    
    
    # 计算除标点外的字符数
    no_punc_count = len([c for c in analysis_text if not re.match(r'[^\w\s]', c)])
    
    st.write(f'字符数: {char_count}')
    st.write(f'除标点外的字符数: {no_punc_count}')
    
    # 导出统计结果
    stats_dict = {'字符数': char_count, '词数': word_count}
    stats_df = pd.DataFrame([stats_dict])
    csv = stats_df.to_csv(encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="下载统计结果",
        data=csv,
        file_name="text_statistics.csv",
        mime="text/csv"
    )

def split_words(analysis_text):
    st.subheader('分词结果')
    
    try:
        # 将文本中的多个空格合并为单个空格
        text = ' '.join(analysis_text.split())
        
        # 分别处理英文和中文
        # 英文：按空格分词，保留标点
        english_pattern = r'[A-Za-z]+(?:\'[A-Za-z]+)*|[.,!?;]'
        english_words = re.findall(english_pattern, text)
        
        # 中文：使用jieba分词
        chinese_text = ''.join(re.findall(r'[\u4e00-\u9fff]+', text))
        chinese_words = jieba.lcut(chinese_text)
        
        # 合并结果
        all_words = english_words + chinese_words
        
        # 显示分词结果
        st.text_area(
            '分词结果（词语间以空格分隔）：',
            value=' '.join(all_words),
            height=200,
            key='split_words_result'
        )
        
        # 提供下载选项
        result_str = ' '.join(all_words)
        st.download_button(
            label="下载分词结果",
            data=result_str.encode('utf-8'),
            file_name="split_words_result.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"分词失败: {str(e)}")

def text_annotation(text, annotation_schema=None):
    """文本标注功能"""
    if not text:
        st.warning('请先输入要标注的文本')
        return
    
    # 使用session_state存储处理后的文本
    if 'processed_text' not in st.session_state:
        st.session_state.processed_text = text
    
    # 文本预处理选项
    st.write("### 文本预处理选项")
    col1, col2, col3 = st.columns(3)
    with col1:
        remove_punctuation = st.checkbox('去除标点符号（保留句号）', key='annotation_remove_punct')
    with col2:
        remove_spaces = st.checkbox('去除多余空格', key='annotation_remove_space')
    with col3:
        remove_numbers = st.checkbox('去除数字', key='annotation_remove_num')
    
    # 文本预处理
    if st.button("应用预处理", key='apply_preprocessing'):
        processed_text = text
        if remove_punctuation:
            # 保留句号、感叹号、问号等分句标点
            processed_text = re.sub(r'[^\w\s。！？!?.]', '', processed_text)
        if remove_spaces:
            # 合并多个空格为单个空格并移除英文单词之间的空格
            words = processed_text.split()
            processed_text = ''.join(words)
        if remove_numbers:
            processed_text = re.sub(r'\d+', '', processed_text)
        
        # 保存处理后的文本
        st.session_state.processed_text = processed_text
        st.success('预处理完成！')
    
    # 显示当前要处理的文本
    st.write("### 当前文本")
    st.text_area("文本内容：", st.session_state.processed_text, height=100, key='current_text_display')
    
    # 分句
    sentences = re.split(r'([。！？.!?])', st.session_state.processed_text)
    sentences = [''.join(i) for i in zip(sentences[0::2], sentences[1::2] + [''])]
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 显示分句结果
    st.write(f"### 共分割出 {len(sentences)} 个句子")
    
    # 标注模式选择
    st.write("### 标注设置")
    annotation_mode = st.radio(
        "选择标注模式：",
        ["词语级标注（标注每个词的类别）", "句子级标注（标注整句的类别）"],
        key="annotation_mode_select"
    )
    
    if annotation_mode == "词语级标注（标注每个词的类别）":
        # 自定义标签
        st.write("设置词语标注的类别，例如：人名、地名、组织名等")
        custom_labels = st.text_input(
            "输入标注类别（用逗号分隔）：",
            value="人名,地名,组织名,时间,其他",
            help="这些类别将用于标注文本中的每个词语",
            key="annotation_custom_labels"
        ).split(',')
        
        # 初始化标注结果
        if 'annotations' not in st.session_state:
            st.session_state.annotations = {}
        
        # 显示标注界面
        st.write("### 词语标注")
        for i, sentence in enumerate(sentences):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"句子 {i+1}: {sentence}")
            with col2:
                # 为每个词创建标注选择
                words = list(jieba.cut(sentence))
                annotations = []
                for j, word in enumerate(words):
                    if word.strip():  # 只标注非空词语
                        unique_key = f"annotation_seq_{i}_{j}_{word}"
                        label = st.selectbox(
                            f"'{word}' 的类别",
                            ["无标注"] + custom_labels,
                            key=unique_key
                        )
                        annotations.append((word, label))
                st.session_state.annotations[i] = annotations
                
    else:  # 句子级标注
        # 自定义类别
        st.write("设置句子标注的类别，例如：积极、消极、中性等")
        custom_categories = st.text_input(
            "输入标注类别（用逗号分隔）：",
            value="积极,消极,中性",
            help="这些类别将用于标注整个句子的属性",
            key="annotation_custom_categories"
        ).split(',')
        
        # 初始化分类结果
        if 'classifications' not in st.session_state:
            st.session_state.classifications = {}
            
        # 显示分类界面
        st.write("### 句子标注")
        for i, sentence in enumerate(sentences):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"句子 {i+1}: {sentence}")
            with col2:
                category = st.selectbox(
                    "选择句子类别",
                    custom_categories,
                    key=f"annotation_cat_{i}"
                )
                st.session_state.classifications[i] = {
                    'text': sentence,
                    'category': category
                }
    
    # 导出标注结果
    if st.button('导出标注结果', key='annotation_export'):
        if annotation_mode == "词语级标注（标注每个词的类别）":
            results = []
            for sent_id, annotations in st.session_state.annotations.items():
                for word, label in annotations:
                    results.append({
                        'sentence_id': sent_id + 1,
                        'word': word,
                        'label': label
                    })
            df = pd.DataFrame(results)
        else:
            df = pd.DataFrame([
                {
                    'sentence_id': k + 1,
                    'text': v['text'],
                    'category': v['category']
                }
                for k, v in st.session_state.classifications.items()
            ])
        
        # 导出为CSV
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="下载标注结果(CSV)",
            data=csv,
            file_name="annotations.csv",
            mime="text/csv",
            key="annotation_download_csv"
        )
        
        # 导出为JSON
        json_str = df.to_json(orient='records', force_ascii=False, indent=2)
        st.download_button(
            label="下载标注结果(JSON)",
            data=json_str.encode('utf-8'),
            file_name="annotations.json",
            mime="application/json",
            key="annotation_download_json"
        )
