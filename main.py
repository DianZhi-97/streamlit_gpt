import openai
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_chat import message
import yaml

# config the page title and icon
st.set_page_config(page_title="ChatGPT", page_icon='🤖')

# use personalized css
def load_css(filepath):
    with open(filepath, 'r') as fID:
        st.markdown(f'<style>{fID.read()}</style>', unsafe_allow_html=True)

load_css('style/style.css')

# load registered user info 
with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

# config the auhenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# start the authenticator
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
else:
    # get OpenAI API key
    with open('openai_apikey.txt', 'r') as fID:
        openai.api_key = fID.readline()

    # init session states
    if 'generated_response' not in st.session_state:
        st.session_state['generated_response'] = []
    if 'past_prompt' not in st.session_state:
        st.session_state['past_prompt'] = []
    if 'conversation' not in st.session_state:
        st.session_state['conversation'] = [
            {'role': 'system', 'content': 'You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.'}]

    # reset the conversation history
    def reset_conversation():
        st.session_state['generated_response'] = []
        st.session_state['past_prompt'] = []
        st.session_state['conversation'] = [
            {'role': 'system', 'content': 'You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.'}]

    # takes a list of conversation and temperature and get response text
    def query(conversation, temperature):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=conversation,
            temperature=temperature)
        return response['choices'][0]['message']['content']

    # use form to gather user input
    def get_input():
        with st.form('get_text_input', clear_on_submit=True):
            user_input = st.text_area('输入对话内容:', '')
            submitted = st.form_submit_button('发送')
        if submitted:
            return user_input

    # sidebar
    with st.sidebar:
        col_left, col_middle, col_right = st.columns([1, 10, 1])
        with col_middle:
            st.subheader(name + ', Welcome:tada:')
            authenticator.logout('退出登陆')
            st.markdown('#')
            temperature = st.slider('Temperature', min_value=0.0, max_value=2.0, value=0.5, step=0.05)
            st.write('Tips: 更高的Temperature会使ChatGPT的回答更加多样化')

    # title + image
    col_left, col_right = st.columns([1,3])
    with col_left:
        st.title('ChatGPT')
    with col_right:
        st.markdown('#####')
        st.image('https://deasilex.com/wp-content/uploads/2022/12/openai.webp', width=100)
    
    st.write('---')

    # description + clear button
    col_left, col_right = st.columns([5,1])
    with col_left:
        st.write('本App直接调用了OpenAI的GPT-3.5 API [OpenAI ChatGPT 入口](https://chat.openai.com/)')
    with col_right:
        btn_pressed = st.button('清空对话', on_click=reset_conversation)
    
    # text input
    user_input = get_input()

    # format and send query to OpenAI API and get response
    if user_input:
        st.session_state.conversation.append({'role': 'user', 'content': user_input})
        output = query(st.session_state.conversation, temperature)
        st.session_state.past_prompt.append(user_input)
        st.session_state.generated_response.append(output)
        st.session_state.conversation.append({'role': 'assistant', 'content': output})

    # display the chat history
    if st.session_state['generated_response']:
        for i in range(len(st.session_state['generated_response'])-1, -1, -1):
            message(st.session_state['generated_response'][i], key=str(i), 
            avatar_style='bottts', seed='ChatGPT')
            message(st.session_state['past_prompt'][i], is_user=True, key=str(i) + '_user', 
            avatar_style='initials', seed=name[0])