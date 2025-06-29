let mediaRecorder;
let audioChunks = [];

function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    mediaRecorder.addEventListener("dataavailable", event => {
      audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener("stop", () => {
      const audioBlob = new Blob(audioChunks);
      const formData = new FormData();
      formData.append("audio_data", audioBlob);

      fetch("/upload", {
        method: "POST",
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        document.getElementById("answer").innerText = "Answer (Original): " + data.answer;
        document.getElementById("translation").innerText = "Translation (English): " + data.translation;
        document.getElementById("nextBtn").disabled = false;
      });

      audioChunks = [];
    });
  });
}

function stopRecording() {
  mediaRecorder.stop();
}
