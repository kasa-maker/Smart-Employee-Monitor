import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="Employee Video Portal", page_icon="🎥")
st.title("🎥 Employee Video Submission")

name = st.text_input("👤 Naam")
user_id = st.text_input("🪪 Employee ID")

# Camera Recording Component
components.html("""
<div style="text-align: center;">
    <video id="preview" width="400" autoplay muted style="border-radius:10px;"></video>
    <br><br>
    <button onclick="startRecording()" 
        style="background:#28a745; color:white; padding:10px 20px; 
               border:none; border-radius:5px; cursor:pointer; margin:5px;">
        🎥 Record Karo
    </button>
    <button onclick="stopRecording()" 
        style="background:#dc3545; color:white; padding:10px 20px; 
               border:none; border-radius:5px; cursor:pointer; margin:5px;">
        ⏹ Stop
    </button>
    <br><br>
    <video id="recorded" width="400" controls style="border-radius:10px; display:none;"></video>
    <br>
    <button onclick="uploadVideo()" id="uploadBtn"
        style="background:#007bff; color:white; padding:10px 20px; 
               border:none; border-radius:5px; cursor:pointer; display:none; margin-top:10px;">
        ⬆️ Upload Karo
    </button>
    <p id="status" style="color:green; font-weight:bold;"></p>
</div>

<script>
let mediaRecorder;
let recordedChunks = [];
let stream;

// Camera start karo
async function startRecording() {
    recordedChunks = [];
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    document.getElementById('preview').srcObject = stream;

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) recordedChunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: 'video/mp4' });
        const url = URL.createObjectURL(blob);
        const recorded = document.getElementById('recorded');
        recorded.src = url;
        recorded.style.display = 'block';
        document.getElementById('uploadBtn').style.display = 'inline-block';
        stream.getTracks().forEach(track => track.stop());
    };

    // 10 second baad automatically stop
    mediaRecorder.start();
    document.getElementById('status').innerText = "⏺ Recording... (10 sec max)";
    setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            document.getElementById('status').innerText = "✅ Recording complete!";
        }
    }, 10000);
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        document.getElementById('status').innerText = "✅ Recording complete!";
    }
}

async function uploadVideo() {
    const name = window.parent.document.querySelectorAll('input')[0].value;
    const userId = window.parent.document.querySelectorAll('input')[1].value;

    if (!name || !userId) {
        document.getElementById('status').innerText = "❌ Pehle Naam aur ID bharo!";
        return;
    }

    const blob = new Blob(recordedChunks, { type: 'video/mp4' });
    const formData = new FormData();
    formData.append('video', blob, 'recorded.mp4');
    formData.append('name', name);
    formData.append('user_id', userId);

    document.getElementById('status').innerText = "⏳ Upload ho raha hai...";

    const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        document.getElementById('status').innerText = "🎉 Data save ho gaya!";
    } else {
        const err = await response.json();
        document.getElementById('status').innerText = "❌ " + err.detail;
    }
}
</script>
""", height=600)