import openai
import json
import streamlit as st
import streamlit_authenticator as stauth
from datetime import date
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text="", display_method='markdown'):
        self.container = container
        self.text = initial_text
        self.display_method = display_method
        self.new_sentence = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.new_sentence += token

        display_function = getattr(self.container, self.display_method, None)
        if display_function is not None:
            display_function(self.text)
        else:
            raise ValueError(f"[-] Invalid display_method: {self.display_method}")

    def on_llm_end(self, response, **kwargs) -> None:
        self.text=""


# config the page title and icon
st.set_page_config(page_title='ChatGPT', page_icon='', layout='wide')

# format page styles
style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* div[data-testid="column"] {text-align: center} */
/* div[data-testid="stVerticalBlock"] > * {text-align: center} */
</style>
'''
st.markdown(style, unsafe_allow_html=True)

# load registered user info
credentials = json.loads(st.secrets['authetications']['credentials'])

# config the auhenticator
authenticator = stauth.Authenticate(
    credentials,
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days']
)

# start the authenticator
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    # st.error('Username/password is incorrect')
    st.error('用户名/密码不正确')
elif authentication_status == None:
    # st.warning('Please enter your username and password')
    st.warning('请输入您的用户名和密码')
else:
    # get OpenAI API key
    openai.api_key = st.secrets['openai_apikey']

    def reset_conversation():
        st.session_state.messages = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # sidebar
    with st.sidebar:
        col_left, col_right = st.columns(2)
        with col_left:
            # st.subheader(name + ', Welcome:tada:')
            st.subheader(name + '，欢迎:tada:')
        with col_right:
            # authenticator.logout('Logout')
            authenticator.logout('退出登录')
        # st.selectbox('Select large language model', ('gpt-4', 'gpt-3.5-turbo'), key='model', on_change=reset_conversation)
        st.selectbox('选择您想使用的大语言模型', ('gpt-4', 'gpt-3.5-turbo'), key='model', on_change=reset_conversation)
        # temperature = st.slider('Temperature', min_value=0.0, max_value=2.0, value=0.0, step=0.1, key='temperature')
        temperature = st.slider('温度', min_value=0.0, max_value=2.0, value=0.0, step=0.1, key='temperature')
        # st.write('Tips: Higher temperatures introduce more randomness, resulting in creative yet potentially less coherent output.')
        st.write('提示：较高的温度会引入更多的随机性')

        # custom_instructions = st.text_area("Custom Instructions", value=f"You are {st.session_state.model.replace('-', ' ').upper()}, a large language model trained by OpenAI.")
        custom_instructions = st.text_area("自定义指令", value=f"你是 {st.session_state.model.replace('-', ' ').upper()}， 一个由OpenAI创造的大语言模型。")
        col_left, col_right = st.columns(2)
        with col_left:
            # st.button('Start New Chat', on_click=reset_conversation)
            st.button('重置对话', on_click=reset_conversation)
        with col_right:
            # st.download_button("Download Chat", f"system: {custom_instructions}\n"+"\n".join([f"{msg.role}: {msg.content}" for msg in st.session_state.messages]), file_name=f"chat_history_{str(date.today())}_{st.session_state.model}.txt")
            st.download_button("下载对话", f"system: {custom_instructions}\n"+"\n".join([f"{msg.role}: {msg.content}" for msg in st.session_state.messages]), file_name=f"chat_history_{str(date.today())}_{st.session_state.model}.txt")

    st.title(f"💬 OpenAI {st.session_state.model.replace('-', ' ').upper()}") 
    
    for msg in st.session_state.messages:
        st.chat_message(msg.role).write(msg.content)

    if prompt := st.chat_input(disabled=False, key="chat_input"):
        st.chat_input(disabled=True, key="disabled_chat_input")
        st.session_state.messages.append(ChatMessage(role="user", content=prompt))
        st.chat_message("user").write(prompt)

    if len(st.session_state.messages) > 0 and st.session_state.messages[-1].role != "assistant":
        with st.chat_message("assistant"):
            assistant_message_placeholder = st.empty()
        stream_handler = StreamHandler(assistant_message_placeholder)
        llm = ChatOpenAI(openai_api_key=st.secrets['openai_apikey'], streaming=True, callbacks=[stream_handler])
        response = llm([ChatMessage(role='system', content=custom_instructions)] + st.session_state.messages)
        st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))
        st.rerun()