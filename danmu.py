def display_danmu(danmu_list):
    if not danmu_list:
        st.warning('未获取到任何弹幕数据')
    else:
        st.subheader('获取到的弹幕数据')
        # 直接显示弹幕数据,不需要展开
        st.write(danmu_list)
        
        # 提供下载弹幕数据的选项
        danmu_df = pd.DataFrame(danmu_list, columns=['弹幕内容'])
        csv = danmu_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="下载弹幕数据",
            data=csv,
            file_name='danmu_data.csv',
            mime='text/csv',
        ) 