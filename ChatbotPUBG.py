import streamlit as st
import google.generativeai as genai
import time
import requests
import re
import random


# Configure the API key
genai.configure(api_key="AIzaSyCC1BWSXF1X5IzgmLzJHh5eTzOaJOoWow0")

# Set up the model
generation_config = {
    "temperature": 0,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


# Check img
def is_valid_image(url):
    try:
        # Gửi yêu cầu HEAD để chỉ lấy headers mà không tải toàn bộ nội dung
        response = requests.head(url, allow_redirects=True, timeout=0.1)
        
        # Kiểm tra nếu response status là 200 và kiểu nội dung là hình ảnh
        if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
            return True
        return False
    except requests.RequestException as e:
        # print(f"Error checking image URL: {e}")
        return False

# Set up the chat
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])


# Streamlit app
def typing_effect(text, placeholder, delay=0.1):
    """Display text one character at a time with a delay using a placeholder."""
    displayed_text = ""
    for char in text:
        displayed_text += char
        # Update the placeholder with large text
        placeholder.markdown(f"<h1 style='text-align:center;'>{displayed_text}</h1>", unsafe_allow_html=True)
        time.sleep(delay)

# Create a placeholder where the title will appear
title_placeholder = st.empty()

# Session state to track if the typing effect has been triggered
if "typing_effect_triggered" not in st.session_state:
    st.session_state.typing_effect_triggered = False

if not st.session_state.typing_effect_triggered:
    typing_effect("PUBG ChatBot", title_placeholder, delay=0.1)
    st.session_state.typing_effect_triggered = True

# Kiểm tra xem đã khởi tạo session chưa
if "initialized" not in st.session_state:
    # Gửi tin nhắn đến chatbot mà không hiển thị trên giao diện
    _ = st.session_state.chat.send_message("Bạn là một chuyên gia về PUBG, hãy dành toàn bộ bộ nhớ và khả năng xử lý chỉ liên quan đến PUBG để tăng hiệu suất làm việc ! Chỉ trả lời các câu hỏi liên quan đến PUBG. Nếu ngoài PUBG thì không cần trả lời !")
    # Đánh dấu là đã khởi tạo
    st.session_state.initialized = True

# Tạo thanh công cụ
with st.sidebar:
    # Add button for a new chat session
    if st.button("Đoạn chat mới"):
        # Reset chat state
        st.session_state.chat = model.start_chat(history=[])
        response = st.session_state.chat.send_message("Bạn là một chuyên gia về PUBG, hãy dành toàn bộ bộ nhớ và khả năng xử lý chỉ liên quan đến PUBG để tăng hiệu suất làm việc ! Chỉ trả lời các câu hỏi liên quan đến PUBG. Nếu ngoài PUBG thì không cần trả lời !")
        # Reset other states
        st.session_state.uploaded_file = None  # Reset file state
        st.session_state.showing_content = False  # Reset content display state
        st.session_state.selected_option = "Không chọn"  # Reset selected option
        st.session_state.typing_effect_triggered = False
        typing_effect("PUBG ChatBot", title_placeholder, delay=0.1)
        st.rerun()  # Refresh the page to reflect changes
    
    st.title("Công cụ hỗ trợ")
    
    # Tạo các lựa chọn trong thanh công cụ với tùy chọn không chọn nào
    selected_option = st.radio(
        "Chọn chức năng:",
        ["Không chọn", "Cách chơi", "Vũ khí", "Chiến thuật", "Bản đồ"]
    )

    # Nút để hiển thị nội dung
    show_content = st.button("Hiển thị nội dung")

# Khởi tạo trạng thái trong session_state nếu chưa có
if 'showing_content' not in st.session_state:
    st.session_state.showing_content = False

# Cập nhật trạng thái khi người dùng nhấn nút
if show_content:
    st.session_state.showing_content = True

# User input
user_input = st.chat_input("Type your message here...")

temp_weapon_name = ""

if user_input:
    user_input = user_input
    
    st.chat_message("user").markdown(user_input)

    # Generate response
    response = st.session_state.chat.send_message(user_input + ". Nếu không liên quan đến PUBG thì không cần trả lời !")
    
    # Display assistant response
    with st.chat_message("assistant"):
        check = response.text.lower()
        image_url = f""
        response_placeholder = st.empty()
        displayed_text = ""
        for i in response.text:
            displayed_text += i
            response_placeholder.markdown(displayed_text)
            time.sleep(0.01)
        if ("súng" or "vũ khí") in check:
            # Replace "(giá trị)" with the actual weapon name dynamically
            weapon_temp = response.text
            weapon_text = weapon_temp.split()
            for i, weapon_p in enumerate(weapon_text):
                weapon_name = weapon_p.strip().lower()  # This value can be based on user input or another source
                weapon_name = re.sub(r"[^\w\s-]", "", weapon_name)
                if weapon_name == "ump":
                    weapon_name = "ump45"
                elif weapon_name == "qbz":
                    weapon_name = "qbz95"
                elif weapon_name == "aug":
                    weapon_name = "aug_a3"
                elif weapon_name == "famas":
                    weapon_name = "famas_g2"
                if i + 1 < len(weapon_text):
                    two_weapon = weapon_name + '_' + weapon_text[i + 1].strip().lower()
                    two_weapon = two_weapon.strip().lower()
                    image_url = f"https://wstatic-prod.pubg.com/web/live/static/game-info/weapons/images/viewer/img-weapons-{two_weapon}.png"
                    if is_valid_image(image_url):
                        text_temp = "\nĐang tạo ảnh xin vui lòng chờ..."
                        for i in text_temp:
                            displayed_text += i
                            response_placeholder.markdown(displayed_text)
                            time.sleep(0.01)
                        st.image(image_url, caption=two_weapon.upper(), use_container_width=True)
                        break
                image_url = f"https://wstatic-prod.pubg.com/web/live/static/game-info/weapons/images/viewer/img-weapons-{weapon_name}.png"
                if is_valid_image(image_url):
                    text_temp = "\nĐang tạo ảnh xin vui lòng chờ..."
                    for i in text_temp:
                        displayed_text += i
                        response_placeholder.markdown(displayed_text)
                        time.sleep(0.01)
                    st.image(image_url, caption=weapon_name.upper(), use_container_width=True)
                    break
        elif "xe" in check:
            veh_text = response.text.split()
            for i in veh_text:
                veh_name = i.strip().lower()
                image_url = f"https://wstatic-prod.pubg.com/web/live/static/game-info/vehicles/images/viewer/img-vehicles-{veh_name}.png"
                if is_valid_image(image_url):
                    text_temp = "\nĐang tạo ảnh xin vui lòng chờ..."
                    for i in text_temp:
                        displayed_text += i
                        response_placeholder.markdown(displayed_text)
                        time.sleep(0.01)
                    st.image(image_url, caption=veh_name.upper(), use_container_width=True)
                    break
        elif "bản đồ" in check:
            map_text = response.text.split()
            list_map = {"erangel":"https://wstatic-prod.pubg.com/web/live/main_eb92790/img/9b5d63e.jpg", "miramar":"https://wstatic-prod.pubg.com/web/live/main_eb92790/img/b5c3c7f.jpg", "sanhok":"https://wstatic-prod.pubg.com/web/live/main_eb92790/img/3ab566e.jpg", "vikendi":"https://wstatic-prod.pubg.com/web/live/main_eb92790/img/1bee462.jpg", "taego":"https://wstatic-prod.pubg.com/web/live/main_eb92790/img/0d771c0.jpg", "deston":"https://wstatic-prod.pubg.com/web/live/main_eb92790/img/b2d4a73.jpg"}
            for i in map_text:
                map_name = i.strip().lower()
                if map_name in list_map:
                    image_url = list_map[map_name]
                    text_temp = "\nĐang tạo ảnh xin vui lòng chờ..."
                    for i in text_temp:
                        displayed_text += i
                        response_placeholder.markdown(displayed_text)
                        time.sleep(0.01)
                    st.image(image_url, caption=map_name.upper(), use_container_width=True)
                    break

# Hiển thị nội dung nếu người dùng đã nhấn nút và có lựa chọn

if st.session_state.showing_content:
    st.markdown("<div class='container'>", unsafe_allow_html=True)

    if selected_option == "Không chọn":
        # Gửi tin nhắn đến chatbot mà không hiển thị trên giao diện
        response = st.session_state.chat.send_message("Bạn là một chuyên gia về PUBG, hãy dành toàn bộ bộ nhớ và khả năng xử lý chỉ liên quan đến PUBG để tăng hiệu suất làm việc ! Chỉ trả lời các câu hỏi liên quan đến PUBG. Nếu ngoài PUBG thì không cần trả lời !")

        typing_effect("PUBG ChatBot", title_placeholder, delay=0.1)

    elif selected_option == "Cách chơi":
        response = st.session_state.chat.send_message("Bạn là một chuyên gia về PUBG. Chỉ trả lời các câu hỏi liên quan đến cách chơi của PUBG và hãy nâng cấp lên chỉ chuyên về cách chơi để tối ưu hơn không cần các dữ liệu ngoài cách chơi. Nếu không liên quan đến PUBG thì không cần trả lời !")
        st.header("Cách chơi PUBG")
        st.subheader("Hướng dẫn cơ bản")
        st.write("Trong PUBG, mục tiêu là trở thành người chơi cuối cùng sống sót. Bạn cần tìm vũ khí, trang bị và hạ gục các đối thủ khác.")
        st.write("Để di chuyển, sử dụng các phím mũi tên hoặc WASD. Nhấn phím Ctrl để nằm, phím Shift để chạy và phím Space để nhảy.")
        st.write("Khi gặp đối thủ, hãy ngắm bằng chuột trái và bắn bằng chuột phải.")

    elif selected_option == "Vũ khí":
        # Dữ liệu về vũ khí

        response = st.session_state.chat.send_message("Bạn là một chuyên gia về PUBG. Chỉ trả lời các câu hỏi liên quan đến vũ khí (bao gồm cả các loại giáp, balo và các phương tiện) của PUBG và hãy nâng cấp lên chỉ chuyên về vũ khí để tối ưu hơn không cần các dữ liệu ngoài vũ khí. Nếu không liên quan đến PUBG thì không cần trả lời !")

        st.title("PUBG Weapon Information")
        
        weapon_data = {"Vui lòng chọn loại vũ khí và vũ khí bạn cần hỗ trợ.":{"Hiện đang không chọn !":0}}
        
        # Chọn vũ khí
        weapon_data.update({
            "AR": {
                "Hiện đang không chọn !": 0,
                "M16A4": {"damage": 37, "speed": 83, "stability": 40, "dps": 66, "range": 59},
                "M416": {"damage": 40, "speed": 70, "stability": 43, "dps": 68, "range": 51},
                "SCAR-L": {"damage": 41, "speed": 65, "stability": 47, "dps": 66, "range": 50},
                "G36C": {"damage": 39, "speed": 68, "stability": 45, "dps": 64, "range": 49},
                "QBZ95": {"damage": 42, "speed": 66, "stability": 44, "dps": 67, "range": 48},
                "K2": {"damage": 40, "speed": 69, "stability": 42, "dps": 67, "range": 52},
                "AUG_A3": {"damage": 44, "speed": 72, "stability": 50, "dps": 69, "range": 55},
                "FAMAS_G2": {"damage": 45, "speed": 75, "stability": 40, "dps": 72, "range": 46},
                "AKM": {"damage": 47, "speed": 60, "stability": 35, "dps": 73, "range": 53},
                "Beryl_M762": {"damage": 46, "speed": 62, "stability": 37, "dps": 71, "range": 51},
                "Groza": {"damage": 48, "speed": 63, "stability": 38, "dps": 75, "range": 54}
            },
            "DMR": {
                "Hiện đang không chọn !": 0,
                "Mini14": {"damage": 46, "speed": 75, "stability": 60, "dps": 52, "range": 70},
                "QBU88": {"damage": 48, "speed": 70, "stability": 65, "dps": 53, "range": 72},
                "Mk12": {"damage": 50, "speed": 72, "stability": 62, "dps": 55, "range": 75},
                "SKS": {"damage": 53, "speed": 68, "stability": 55, "dps": 58, "range": 70},
                "SLR": {"damage": 58, "speed": 65, "stability": 50, "dps": 61, "range": 75},
                "Mk14": {"damage": 61, "speed": 60, "stability": 45, "dps": 64, "range": 78},
                "VSS": {"damage": 38, "speed": 80, "stability": 70, "dps": 45, "range": 50},
                "Dragunov": {"damage": 60, "speed": 58, "stability": 48, "dps": 62, "range": 80}
            },
            "SMG": {
                "Hiện đang không chọn !": 0,
                "Tommy_Gun": {"damage": 40, "speed": 75, "stability": 50, "dps": 60, "range": 30},
                "UMP45": {"damage": 39, "speed": 70, "stability": 60, "dps": 58, "range": 35},
                "Micro_UZI": {"damage": 26, "speed": 95, "stability": 40, "dps": 68, "range": 25},
                "Vector": {"damage": 31, "speed": 90, "stability": 45, "dps": 72, "range": 28},
                "PP-19_Bizon": {"damage": 35, "speed": 80, "stability": 55, "dps": 62, "range": 32},
                "MP5K": {"damage": 33, "speed": 85, "stability": 58, "dps": 65, "range": 30},
                "MP9": {"damage": 34, "speed": 88, "stability": 50, "dps": 66, "range": 28},
                "P90": {"damage": 37, "speed": 85, "stability": 65, "dps": 67, "range": 40}
            },
            "SR": {
                "Hiện đang không chọn !": 0,
                "Kar98k": {"damage": 79, "speed": 60, "stability": 35, "dps": 50, "range": 80},
                "MOSIN_NAGANT": {"damage": 79, "speed": 60, "stability": 36, "dps": 51, "range": 80},
                "M24": {"damage": 82, "speed": 58, "stability": 40, "dps": 52, "range": 85},
                "AWM": {"damage": 100, "speed": 50, "stability": 30, "dps": 60, "range": 100},
                "Win94": {"damage": 66, "speed": 70, "stability": 50, "dps": 45, "range": 65},
                "Lynx_AMR": {"damage": 100, "speed": 45, "stability": 25, "dps": 70, "range": 100}
            },
            "Pistols": {
                "Hiện đang không chọn !": 0,
                "P1911": {"damage": 35, "speed": 75, "stability": 50, "dps": 60, "range": 25},
                "P92": {"damage": 33, "speed": 80, "stability": 55, "dps": 58, "range": 30},
                "P18C": {"damage": 23, "speed": 90, "stability": 40, "dps": 65, "range": 20},
                "R1895": {"damage": 50, "speed": 50, "stability": 45, "dps": 50, "range": 25},
                "Skorpion": {"damage": 28, "speed": 85, "stability": 45, "dps": 62, "range": 20},
                "DEagle": {"damage": 62, "speed": 40, "stability": 30, "dps": 58, "range": 35}
            },
            "Shotgun": {
                "Hiện đang không chọn !": 0,
                "S12K": {"damage": 22, "speed": 45, "stability": 55, "dps": 100, "range": 25},
                "S1897": {"damage": 26, "speed": 35, "stability": 50, "dps": 91, "range": 30},
                "S686": {"damage": 26, "speed": 40, "stability": 52, "dps": 90, "range": 30},
                "DBS": {"damage": 26, "speed": 45, "stability": 58, "dps": 98, "range": 25},
                "SAWED_OFF": {"damage": 25, "speed": 30, "stability": 48, "dps": 80, "range": 15},
                "O12": {"damage": 20, "speed": 50, "stability": 60, "dps": 100, "range": 20}
            },
            "LMG": {
                "Hiện đang không chọn !": 0,
                "MG3": {"damage": 40, "speed": 75, "stability": 50, "dps": 80, "range": 65},
                "DP28": {"damage": 51, "speed": 55, "stability": 60, "dps": 70, "range": 60},
                "M249": {"damage": 45, "speed": 70, "stability": 55, "dps": 78, "range": 62}
            },
            "Melee": {
                "Hiện đang không chọn !": 0,
                "Crowbar": {"damage": 40, "speed": 30, "stability": 50, "range": 10, "dps": 0},
                "Machete": {"damage": 45, "speed": 35, "stability": 40, "range": 8, "dps": 0},
                "Pan": {"damage": 50, "speed": 25, "stability": 70, "range": 6, "dps": 0},
                "Sickle": {"damage": 35, "speed": 40, "stability": 45, "range": 9, "dps": 0},
                "Pickaxe": {"damage": 55, "speed": 20, "stability": 60, "range": 7, "dps": 0}
            },
            "Throwables": {
                "Hiện đang không chọn !": 0,
                "Stun_Grenade": {"damage": 0, "blast_radius": 8, "effect_duration": 3, "type_": "Choáng"},
                "Frag_Grenade": {"damage": 80, "blast_radius": 10, "effect_duration": 0, "type_": "Nổ"},
                "Molotov_Cocktail": {"damage": 40, "blast_radius": 5, "effect_duration": 7, "type_": "Lửa"},
                "Smoke_Grenade": {"damage": 0, "blast_radius": 12, "effect_duration": 10, "type_": "Khói"},
                "C4": {"damage": 100, "blast_radius": 25, "effect_duration": 0, "type_": "Nổ mạnh"},
            },
        })

        # Người dùng chọn loại vũ khí
        weapon_type = st.selectbox("Chọn loại vũ khí:", options=list(weapon_data.keys()))

        # Lấy danh sách các vũ khí từ loại vũ khí đã chọn
        weapon_list = list(weapon_data[weapon_type].keys())

        # Người dùng chọn vũ khí cụ thể
        weapon_name = st.selectbox("Chọn vũ khí:", options=weapon_list)
        
        # Hiển thị thông số vũ khí
        if (weapon_name != "Hiện đang không chọn !" and weapon_type != "Throwables"):
            response = st.session_state.chat.send_message("Thông tin chi tiết về " + ("vũ khí cận chiến " if weapon_type == "Melee" else "súng ") + weapon_name)

            # Display assistant response
            with st.chat_message("assistant"):
                check = response.text.lower()
                image_url = f""
                response_placeholder = st.empty()
                displayed_text = ""
                for i in response.text:
                    displayed_text += i
                    response_placeholder.markdown(displayed_text)
                    time.sleep(0.01)
            
            image_url = f"https://wstatic-prod.pubg.com/web/live/static/game-info/weapons/images/viewer/img-weapons-{weapon_name}.png"
            # image_url = f"https://wstatic-prod.pubg.com/web/live/static/game-info/weapons/images/viewer/img-weapons-m16a4.png"
            if is_valid_image(image_url):
                text_temp = "\nĐang tạo ảnh xin vui lòng chờ..."
                for i in text_temp:
                    displayed_text += i
                    response_placeholder.markdown(displayed_text)
                    time.sleep(0.01)
                st.image(image_url, caption=weapon_name.upper(), use_container_width=True)
            
            st.header(f"Details for {weapon_name}")
            weapon_info = weapon_data[weapon_type][weapon_name]
            st.write(f"Sát thương: ")
            st.progress(int(weapon_info['damage']) / 100)
            st.write(f"Tốc độ bắn: ")
            st.progress(int(weapon_info['speed']) / 100)
            st.write(f"Độ ổn định: ")
            st.progress(int(weapon_info['stability']) / 100)
            st.write(f"Sát thương trên giây: ")
            st.progress(int(weapon_info['dps']) / 100)
            st.write(f"Phạm vi bắn: ")
            st.progress(int(weapon_info['range']) / 100)
        
            image_url = f"https://wstatic-prod.pubg.com/web/live/static/game-info/weapons/images/viewer/img-weapons-{weapon_name.lower()}.png"
            st.image(image_url, caption=weapon_name.upper(), use_container_width=True)
        elif (weapon_name != "Hiện đang không chọn !" and weapon_type == "Throwables"):

            response = st.session_state.chat.send_message("Thông tin ngắn gọn về " + weapon_name)

            # Display assistant response
            with st.chat_message("assistant"):
                check = response.text.lower()
                image_url = f""
                response_placeholder = st.empty()
                displayed_text = ""
                for i in response.text:
                    displayed_text += i
                    response_placeholder.markdown(displayed_text)
                    time.sleep(0.01)
            
            image_url = f"https://wstatic-prod.pubg.com/web/live/static/game-info/weapons/images/viewer/img-weapons-{weapon_name}.png"
            # image_url = f"https://wstatic-prod.pubg.com/web/live/static/game-info/weapons/images/viewer/img-weapons-m16a4.png"
            if is_valid_image(image_url):
                text_temp = "\nĐang tạo ảnh xin vui lòng chờ..."
                for i in text_temp:
                    displayed_text += i
                    response_placeholder.markdown(displayed_text)
                    time.sleep(0.01)
                st.image(image_url, caption=weapon_name.upper(), use_container_width=True)
            
            st.header(f"Details for {weapon_name}")
            weapon_info = weapon_data[weapon_type][weapon_name]
            st.write(f"Sát thương: ")
            st.progress(int(weapon_info['damage']) / 100)
            st.write(f"Bán kính hiệu lực: ")
            st.progress(int(weapon_info['blast_radius']) / 100)
            st.write(f"Thời gian hiệu lực: ")
            st.progress(int(weapon_info['effect_duration']) / 100)
            st.markdown(f"Loại hiệu ứng: **{weapon_info['type_']}**")
        
            image_url = f"https://wstatic-prod.pubg.com/web/live/static/game-info/weapons/images/viewer/img-weapons-{weapon_name.lower()}.png"
            st.image(image_url, caption=weapon_name.upper(), use_container_width=True)
                

    elif selected_option == "Chiến thuật":

        response = st.session_state.chat.send_message("Bạn là một chuyên gia về PUBG. Chỉ trả lời các câu hỏi liên quan đến chiến thuật của PUBG (bao gồm cả chiến thuật sử dụng các loại vũ khí, vật phẩm, ...) và hãy nâng cấp lên chỉ chuyên về chiến thuật để tối ưu hơn không cần các dữ liệu ngoài chiến thuật. Nếu không liên quan đến PUBG thì không cần trả lời !")

        strategies_data = [
            "Hiện đang không chọn!",
            "Hạ cánh nhanh",
            "Loot đồ hiệu quả",
            "Phòng thủ trong nhà",
            "Di chuyển theo bo",
            "Phục kích",
            "Chiến đấu từ xa",
            "Tấn công xung phong",
            "Đồng đội phối hợp",
            "Kiểm soát phương tiện",
            "Chiến thuật ẩn mình",
            "Chặn cầu",
            "Kiểm soát khu vực cao",
            "Phân tán đội hình",
            "Chiến thuật giả chết",
            "Hỗ trợ đồng đội từ xa",
            "Xâm nhập bo cuối cùng",
            "Giả lập âm thanh đánh lạc hướng",
            "Sử dụng smoke và lựu đạn chiến thuật",
            "Tận dụng súng bắn tỉa",
            "Di chuyển theo mép bo",
            "Săn thính (Drop Hunter)",
            "Chiếm cứ điểm quan trọng",
            "Rút lui chiến thuật",
            "Kiểm soát vật phẩm hiếm",
            "Xây dựng vòng bảo vệ đồng đội",
            "Lấy xe làm lá chắn",
            "Dụ địch vào khu vực nguy hiểm",
            "Chiến thuật chia nhỏ đội hình khi loot",
            "Ưu tiên tiêu diệt sniper đối phương",
            "Tấn công đồng bộ từ nhiều hướng",
        ]

        # Tiêu đề ứng dụng
        st.title("PUBG Strategy Selector")

        # Người dùng chọn chiến thuật
        selected_strategy = st.selectbox("Gợi ý các chiến thuật phổ biến:", options=strategies_data)

        # Hiển thị chiến thuật được chọn
        if selected_strategy != "Hiện đang không chọn!":
            response = st.session_state.chat.send_message("Phân tích chi tiết chiến thuật " + selected_strategy + " và đưa ra cách tận dụng, loại map sử dụng và nhiều cách tận dụng khác.")

            # Display assistant response
            with st.chat_message("assistant"):
                check = response.text.lower()
                image_url = f""
                response_placeholder = st.empty()
                displayed_text = ""
                for i in response.text:
                    displayed_text += i
                    response_placeholder.markdown(displayed_text)
                    time.sleep(0.01)
    elif selected_option == "Bản đồ":

        response = st.session_state.chat.send_message("Bạn là một chuyên gia về PUBG. Chỉ trả lời các câu hỏi liên quan đến bản đồ (bao gồm cả cách chơi bản đồ đó, các thứ liên quan đến bản đồ bao gồm vũ khí có ở bản đồ đó không, ...) của PUBG và hãy nâng cấp lên chỉ chuyên về bản đồ để tối ưu hơn không cần các dữ liệu ngoài bản đồ. Nếu không liên quan đến PUBG thì không cần trả lời !")

        # Dữ liệu về bản đồ
        map_data = {
            "Hiện đang không chọn!": {},
            "Erangel": {
                "size": "8x8 km",
                "locations": ["Pochinki", "School", "Sosnovka Military Base"],
                "climate": "Đồng cỏ, mùa hè",
                "terrain": "Đồi núi và đồng bằng",
                "weapon_suggestions": ["M416", "SCAR-L", "Kar98k"],
                "image_map": "https://wstatic-prod.pubg.com/web/live/main_eb92790/img/9b5d63e.jpg"
            },
            "Miramar": {
                "size": "8x8 km",
                "locations": ["Los Leones", "Pecado", "Hacienda del Patrón"],
                "climate": "Sa mạc",
                "terrain": "Nhiều khu vực mở và đồi cát",
                "weapon_suggestions": ["SLR", "AWM", "M24"],
                "image_map": "https://wstatic-prod.pubg.com/web/live/main_eb92790/img/b5c3c7f.jpg"
            },
            "Sanhok": {
                "size": "4x4 km",
                "locations": ["Paradise Resort", "Bootcamp", "Docks"],
                "climate": "Nhiệt đới",
                "terrain": "Rừng rậm",
                "weapon_suggestions": ["Vector", "Beryl M762", "Groza"],
                "image_map": "https://wstatic-prod.pubg.com/web/live/main_eb92790/img/3ab566e.jpg"
            },
            "Vikendi": {
                "size": "6x6 km",
                "locations": ["Castle", "Cosmodrome", "Mount Kreznic"],
                "climate": "Tuyết",
                "terrain": "Nhiều khu vực ẩn nấp",
                "weapon_suggestions": ["M416", "Kar98k", "SKS"],
                "image_map": "https://wstatic-prod.pubg.com/web/live/main_eb92790/img/1bee462.jpg"
            },
            "Karakin": {
                "size": "2x2 km",
                "locations": ["Bashara", "Hadiqa Nemo", "Al Habar"],
                "climate": "Sa mạc khô cằn",
                "terrain": "Địa hình nhỏ với nhiều hầm ngầm",
                "weapon_suggestions": ["SMG", "Shotgun", "DMR"],
                "image_map": "https://wstatic-prod.pubg.com/web/live/main_eb92790/img/ce6fe02.jpg"
            },
            "Taego": {
                "size": "8x8 km",
                "locations": ["Terminal", "Palace", "Field"],
                "climate": "Mùa hè Đông Á",
                "terrain": "Đồng bằng và làng quê",
                "weapon_suggestions": ["M416", "K2", "Mk12"],
                "image_map": "https://wstatic-prod.pubg.com/web/live/main_eb92790/img/0d771c0.jpg"
            },
            "Livik": {
                "size": "2x2 km",
                "locations": ["Midstein", "Power Plant", "Iceborg"],
                "climate": "Hỗn hợp",
                "terrain": "Địa hình đa dạng: tuyết, đồng cỏ, đồi đá",
                "weapon_suggestions": ["P90", "FAMAS", "Mk14"],
                "image_map": "https://liquipedia.net/commons/images/2/20/PUBG_Mobile_Livik.jpg"
            },
        }

        # Tiêu đề ứng dụng
        st.title("PUBG Map Information")

        # Người dùng chọn bản đồ
        map_name = st.selectbox("Các bản đồ phổ biến:", options=list(map_data.keys()))

        # Hiển thị thông tin về bản đồ
        if map_name != "Hiện đang không chọn!":

            response = st.session_state.chat.send_message("Thông tin chi tiết về " + map_name + ". Bao gồm chiến lược và vũ khí kiến nghị.")

            # Display assistant response
            with st.chat_message("assistant"):
                check = response.text.lower()
                image_url = f""
                response_placeholder = st.empty()
                displayed_text = ""
                for i in response.text:
                    displayed_text += i
                    response_placeholder.markdown(displayed_text)
                    time.sleep(0.01)
            
            st.header(f"Thông tin ngắn gọn về bản đồ: {map_name}")
            
            # Thông tin cơ bản
            map_info = map_data[map_name]
            st.write(f"- **Kích thước:** {map_info['size']}.")
            st.write(f"- **Địa điểm nổi bật:** {', '.join(map_info['locations'])}.")
            st.write(f"- **Khí hậu:** {map_info['climate']}.")
            st.write(f"- **Địa hình:** {map_info['terrain']}.")
            st.write(f"- **Vũ khí được khuyến nghị:** {', '.join(map_info['weapon_suggestions'])}.")
            
            # Hiển thị hình ảnh bản đồ
            map_image_url = f"{map_info['image_map']}"
            st.image(map_image_url, caption=map_name, use_container_width=True)

st.markdown("""
    <style>
        .st-ce {
            border-radius: 20px;
        }
        .st-b1 {
            border-radius: 20px;
        } 
        .stChatInput {
            border-radius: 20px;
        }
        .title {
            font-size: 24px;
            color: blue;
            font-weight: bold;
        }
        .chat-box {
            background-color: #f0f0f0;
            padding: 16px;
            border-radius: 16px;
        }
        .st-bt {
            padding-left: 0.8rem
        }

    </style>
""", unsafe_allow_html=True)

# Css content

css_content = """
<style>
    .mt-5 {
        margin-top: 1.25rem;
    }

    .py-2 {
        padding-bottom: .5rem;
        padding-top: .5rem;
    }

    .px-3 {
        padding-left: .75rem;
        padding-right: .75rem;
    }

</style>

"""
st.markdown(css_content, unsafe_allow_html=True)