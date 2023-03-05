import openai
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_chat import message
import yaml

st.set_page_config(page_title="ChatGPT", page_icon='🤖')

def load_css(filepath):
    with open(filepath, 'r') as fID:
        st.markdown(f'<style>{fID.read()}</style>', unsafe_allow_html=True)

load_css('style/style.css')

with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
else:
    with open('openai_apikey.txt', 'r') as fID:
        openai.api_key = fID.readline()
    if 'generated_response' not in st.session_state:
        st.session_state['generated_response'] = []
    if 'past_prompt' not in st.session_state:
        st.session_state['past_prompt'] = []
    if 'conversation' not in st.session_state:
        st.session_state['conversation'] = [
            {'role': 'system', 'content': 'You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.'}]

    def reset_conversation():
        st.session_state['input'] = ''
        user_input = ''
        st.session_state['generated_response'] = []
        st.session_state['past_prompt'] = []
        st.session_state['conversation'] = [
            {'role': 'system', 'content': 'You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.'}]

    def query(conversation, temperature):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=conversation,
            temperature=temperature)
        return response['choices'][0]['message']['content']

    st.container()

    col_left, col_right = st.columns([1,3])
    with col_left:
        st.title('ChatGPT')
    with col_right:
        st.markdown('#####')
        st.image('https://deasilex.com/wp-content/uploads/2022/12/openai.webp', width=100)
    
    st.write('---')

    col_left, col_right = st.columns([5,1])
    with col_left:
        st.write('本App直接调用了OpenAI的GPT-3.5 API [OpenAI ChatGPT 入口](https://chat.openai.com/)')
    with col_right:
        btn_pressed = st.button('清空对话', on_click=reset_conversation)
    
    user_input = st.text_input('输入对话(回车键发送):' ,'', key='input')
    
    with st.sidebar:
        col_left, col_middle, col_right = st.columns([1, 10, 1])
        with col_middle:
            st.subheader(name + ', Welcome:tada:')
            authenticator.logout('退出登陆')
            st.markdown('#')
            temperature = st.slider('Temperature', min_value=0.0, max_value=2.0, value=0.5, step=0.05)
            st.write('Tips: 更高的Temperature会使ChatGPT的回答更加多样化')

    if user_input:
        st.session_state.conversation.append({'role': 'user', 'content': user_input})
        output = query(st.session_state.conversation, temperature)
        st.session_state.past_prompt.append(user_input)
        st.session_state.generated_response.append(output)
        st.session_state.conversation.append({'role': 'assistant', 'content': output})

    if st.session_state['generated_response']:
        for i in range(len(st.session_state['generated_response'])-1, -1, -1):
            message(st.session_state['generated_response'][i], key=str(i), 
            avatar_style='bottts', seed='ChatGPT')
            message(st.session_state['past_prompt'][i], is_user=True, key=str(i) + '_user', 
            avatar_style='initials', seed=name[0])