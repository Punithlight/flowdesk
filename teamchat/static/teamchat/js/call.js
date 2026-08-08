// call.js
// WebRTC calling + screen share + recording
// Include AFTER script.js


document.addEventListener("DOMContentLoaded", () => {


/* =====================================================
   DOM ELEMENTS
===================================================== */


const csrfToken =
document.querySelector('meta[name="csrf-token"]').content;


const currentUserId =
document.querySelector('meta[name="current-user-id"]').content;


const localVideo =
document.getElementById("localVideo");


const remoteVideo =
document.getElementById("remoteVideo");


const callOverlay =
document.getElementById("callOverlay");


const callTitle =
document.getElementById("callTitle");


const endCallBtn =
document.getElementById("endCallBtn");


const muteBtn =
document.getElementById("muteBtn");


const toggleCameraBtn =
document.getElementById("toggleCameraBtn");


const recordCallBtn =
document.getElementById("recordCallBtn");


const recordingIndicator =
document.getElementById("recordingIndicator");


const recordingTimerEl =
document.getElementById("recordingTimer");


const recordingSaving =
document.getElementById("recordingSaving");



/* =====================================================
   WEBRTC VARIABLES
===================================================== */


const ICE_SERVERS = {

iceServers:[
{
urls:"stun:stun.l.google.com:19302"
}
]

};


let socket = null;

let pc = null;

let localStream = null;

let currentRoom = null;

let currentRecipientForCall = null;


let isMuted = false;

let isCameraOff = false;



/* =====================================================
   MEETING JOIN
===================================================== */


const joinBtn =
document.getElementById("joinMeetingBtn");


if(joinBtn){

joinBtn.addEventListener("click",async()=>{


if(!window.meetingData){

alert("Meeting information missing");

return;

}


currentRoom =
window.meetingData.room;


await startCall({
video:true,
meeting:true
});


});


}




/* =====================================================
   NOTIFICATION SOCKET
===================================================== */


const scheme =
window.location.protocol === "https:"
? "wss"
: "ws";


const notifySocket =
new WebSocket(
`${scheme}://${window.location.host}/ws/notify/`
);



notifySocket.onopen=()=>{

console.log(
"Notification socket connected"
);

};



notifySocket.onerror=(err)=>{

console.error(
"Notification socket error",
err
);

};



notifySocket.onclose=()=>{

console.log(
"Notification socket closed"
);

};





notifySocket.onmessage=async(event)=>{


const data =
JSON.parse(event.data);



console.log(
"Incoming notification:",
data
);



if(data.type==="notify_call"){


const accept =
confirm(
`${data.caller_name} is calling you`
);



if(accept){


currentRoom =
data.room_name;


await startIncomingCall({

video:data.call_type==="video"

});


}


}


};





/* =====================================================
   INCOMING CALL
===================================================== */


async function startIncomingCall({video}){


try{


localStream =
await navigator.mediaDevices.getUserMedia({

audio:true,

video:video

});



localVideo.srcObject =
localStream;



callOverlay.style.display =
"flex";



callTitle.textContent =
video
?
"Incoming Video Call"
:
"Incoming Audio Call";



await createPeerConnection();



socket =
openSignalingSocket(
currentRoom
);



}

catch(err){

alert(
"Could not join call: "
+
err.message
);

}


}






/* =====================================================
   ROOM CALCULATION
===================================================== */


function computeRoomName(){


const recipientId =
window.getCurrentRecipientId
?
window.getCurrentRecipientId()
:
null;



if(!recipientId){

return null;

}



if(
String(recipientId).startsWith("group:")
){

return "group-" +
recipientId.split(":")[1];

}




const ids=[

String(currentUserId),

String(recipientId)

].sort();



return "user-" + ids.join("-");


}






/* =====================================================
   OPEN CALL SOCKET
===================================================== */


function openSignalingSocket(room){



const scheme =
window.location.protocol==="https:"
?
"wss"
:
"ws";



const ws =
new WebSocket(

`${scheme}://${window.location.host}/ws/call/${room}/`

);




ws.onopen=()=>{


console.log(
"Call socket connected",
room
);



ws.send(
JSON.stringify({

type:"join"

})
);


};




ws.onmessage=async(event)=>{


const data =
JSON.parse(event.data);



console.log(
"Signal:",
data
);



await handleSignal(data);


};




ws.onclose=()=>{


console.log(
"Call socket closed"
);


};



return ws;


}
/* =====================================================
   WEBRTC SIGNAL HANDLING
===================================================== */


async function handleSignal(data){


if(!pc){

await createPeerConnection();

}



switch(data.type){



case "join":



// Only one side creates offer
// smaller user id becomes caller

const myId =
Number(currentUserId);


const otherId =
Number(
window.getCurrentRecipientId
?
window.getCurrentRecipientId()
:
0
);



if(
myId > otherId
){

return;

}



if(
pc.signalingState !== "stable"
){

return;

}




const offer =
await pc.createOffer();



await pc.setLocalDescription(
offer
);



socket.send(
JSON.stringify({

type:"offer",

sdp:pc.localDescription

})
);



break;





case "offer":



if(
pc.signalingState !== "stable"
){

console.log(
"Offer ignored"
);

return;

}



await pc.setRemoteDescription(

new RTCSessionDescription(
data.sdp
)

);




const answer =
await pc.createAnswer();



await pc.setLocalDescription(
answer
);



socket.send(
JSON.stringify({

type:"answer",

sdp:pc.localDescription

})
);



break;






case "answer":



if(
pc.signalingState !==
"have-local-offer"
){

return;

}



await pc.setRemoteDescription(

new RTCSessionDescription(
data.sdp
)

);



break;







case "ice":



if(data.candidate){


try{


await pc.addIceCandidate(

new RTCIceCandidate(
data.candidate
)

);


}

catch(err){

console.error(
"ICE error",
err
);

}


}



break;







case "leave":



endCall();


break;



}



}







/* =====================================================
   CREATE PEER CONNECTION
===================================================== */


async function createPeerConnection(){



if(pc){

return pc;

}



pc =
new RTCPeerConnection(
ICE_SERVERS
);





/*
 Send ICE candidates
 */


pc.onicecandidate =
(event)=>{


if(
event.candidate &&
socket
){


socket.send(
JSON.stringify({

type:"ice",

candidate:event.candidate

})
);


}


};






/*
 Receive remote video/audio
 */


pc.ontrack =
(event)=>{


console.log(
"Remote stream received"
);



remoteVideo.srcObject =
event.streams[0];


};






/*
 Add local tracks
 */


if(localStream){


localStream
.getTracks()
.forEach(
track=>{


pc.addTrack(
track,
localStream
);


});

}



return pc;


}









/* =====================================================
   START CALL
===================================================== */


async function startCall({
video=false,
meeting=false
}){



let room;



/*
 Meeting call
 */


if(
meeting &&
window.meetingData
){


room =
window.meetingData.room;


}

else{


room =
computeRoomName();


}






if(!room){


alert(
"Select contact first"
);


return;


}



currentRoom =
room;






currentRecipientForCall =
window.getCurrentRecipientId
?
window.getCurrentRecipientId()
:
null;






// Notify backend

await fetch(
"/teamchat/call/start/",
{

method:"POST",

headers:{

"Content-Type":
"application/json",

"X-CSRFToken":
csrfToken

},


body:JSON.stringify({

recipient_id:
currentRecipientForCall,

room_name:
room,

call_type:
video
?
"video"
:
"audio"

})


}

);







try{


localStream =
await navigator.mediaDevices.getUserMedia({

audio:true,

video:video

});


}

catch(err){


alert(
"Camera/Microphone error: "
+
err.message
);


return;


}





localVideo.srcObject =
localStream;



callOverlay.style.display =
"flex";



callTitle.textContent =
video
?
"Video Call"
:
"Audio Call";




resetCallControlsUI();



await createPeerConnection();



socket =
openSignalingSocket(
room
);



}









/* =====================================================
   SCREEN SHARE CALL
===================================================== */


async function startScreenShareCall(){



let room =
computeRoomName();



if(!room){


alert(
"Select contact first"
);


return;


}



currentRoom =
room;



currentRecipientForCall =
window.getCurrentRecipientId
?
window.getCurrentRecipientId()
:
null;





try{


localStream =
await navigator.mediaDevices.getDisplayMedia({

video:true,

audio:true

});


}

catch(err){


alert(
"Screen share failed: "
+
err.message
);


return;


}





localVideo.srcObject =
localStream;



callOverlay.style.display =
"flex";



callTitle.textContent =
"Screen Sharing";



resetCallControlsUI();



await createPeerConnection();



socket =
openSignalingSocket(
room
);





const videoTrack =
localStream.getVideoTracks()[0];



if(videoTrack){


videoTrack.onended =
()=>{

endCall();

};


}



}
/* =====================================================
   RECORDING
===================================================== */


let mediaRecorder = null;

let recordedChunks = [];

let recordingCanvas = null;

let recordingCtx = null;

let recordingRAF = null;

let recordingAudioCtx = null;

let recordingTimerInterval = null;

let recordingStartedAt = null;

let isRecording = false;



function formatTimer(seconds){


const min =
Math.floor(seconds / 60)
.toString()
.padStart(2,"0");


const sec =
Math.floor(seconds % 60)
.toString()
.padStart(2,"0");



return `${min}:${sec}`;


}





function drawRecordingFrame(){


if(!recordingCtx)
return;



const w =
recordingCanvas.width;


const h =
recordingCanvas.height;



recordingCtx.fillStyle="#000";


recordingCtx.fillRect(
0,
0,
w,
h
);



if(
remoteVideo.readyState >= 2
){


recordingCtx.drawImage(
remoteVideo,
0,
0,
w,
h
);


}




if(
localVideo.readyState >=2
){


const pipW =
w*0.25;


const ratio =
localVideo.videoHeight /
(localVideo.videoWidth || 1);



const pipH =
pipW *
(ratio || 0.75);



recordingCtx.drawImage(

localVideo,

w-pipW-20,

h-pipH-20,

pipW,

pipH

);


}



recordingRAF =
requestAnimationFrame(
drawRecordingFrame
);


}







function buildRecordingAudio(){


recordingAudioCtx =
new AudioContext();



const destination =
recordingAudioCtx
.createMediaStreamDestination();




if(localStream){


const localAudio =
localStream
.getAudioTracks();



if(localAudio.length){


const source =
recordingAudioCtx
.createMediaStreamSource(

new MediaStream(localAudio)

);



source.connect(
destination
);


}

}





if(remoteVideo.srcObject){


const remoteAudio =
remoteVideo.srcObject
.getAudioTracks();



if(remoteAudio.length){


const source =
recordingAudioCtx
.createMediaStreamSource(

new MediaStream(remoteAudio)

);



source.connect(
destination
);


}


}



return destination.stream;


}








function startRecording(){



if(isRecording)
return;



if(!remoteVideo.srcObject){


alert(
"Wait for another user to join"
);


return;


}




recordingCanvas =
document.createElement(
"canvas"
);


recordingCanvas.width =
1280;


recordingCanvas.height =
720;



recordingCtx =
recordingCanvas
.getContext(
"2d"
);





const videoStream =
recordingCanvas
.captureStream(
30
);



const audioStream =
buildRecordingAudio();





const mixedStream =
new MediaStream([

...videoStream.getVideoTracks(),

...audioStream.getAudioTracks()

]);





let mimeType =
"video/webm;codecs=vp9,opus";



if(
!MediaRecorder.isTypeSupported(
mimeType
)
){


mimeType =
"video/webm;codecs=vp8,opus";


}




mediaRecorder =
new MediaRecorder(
mixedStream,
{
mimeType
}
);




recordedChunks=[];




mediaRecorder.ondataavailable =
(e)=>{


if(
e.data.size>0
){

recordedChunks.push(e.data);

}


};





mediaRecorder.onstop =
uploadRecording;




mediaRecorder.start(
1000
);



drawRecordingFrame();



isRecording=true;



recordingStartedAt =
Date.now();



recordingIndicator.style.display =
"flex";



recordingTimerEl.textContent =
"00:00";



recordingTimerInterval =
setInterval(()=>{


recordingTimerEl.textContent =
formatTimer(

(Date.now()-recordingStartedAt)
/1000

);


},500);





recordCallBtn.classList.add(
"recording-on"
);



}









function stopRecording(){



if(!isRecording)
return;



isRecording=false;




if(mediaRecorder &&
mediaRecorder.state!=="inactive"
){


mediaRecorder.stop();


}




if(recordingRAF){


cancelAnimationFrame(
recordingRAF
);


recordingRAF=null;


}




if(recordingTimerInterval){


clearInterval(
recordingTimerInterval
);


recordingTimerInterval=null;


}





if(recordingAudioCtx){


recordingAudioCtx.close();


recordingAudioCtx=null;


}




recordingIndicator.style.display =
"none";



recordCallBtn.classList.remove(
"recording-on"
);



}









async function uploadRecording(){



const blob =
new Blob(
recordedChunks,
{
type:"video/webm"
}
);



if(blob.size===0)
return;




recordingSaving.style.display =
"block";





const formData =
new FormData();



formData.append(
"file",
blob,
`call-${Date.now()}.webm`
);



formData.append(
"room_name",
currentRoom
);



formData.append(
"duration",
Math.floor(
(Date.now()-recordingStartedAt)
/1000
)
);






try{


await fetch(
"/teamchat/recordings/upload/",
{

method:"POST",

headers:{

"X-CSRFToken":
csrfToken

},

body:formData


}

);



if(
window.loadRecordings
){

window.loadRecordings();

}



}

catch(err){


console.error(
"Recording upload error",
err
);


}

finally{


recordingSaving.style.display =
"none";


}



}










/* =====================================================
   CALL CONTROLS
===================================================== */


function resetCallControlsUI(){



isMuted=false;

isCameraOff=false;



muteBtn.innerHTML =
'<i class="fa-solid fa-microphone"></i>';



toggleCameraBtn.innerHTML =
'<i class="fa-solid fa-video"></i>';



}









function endCall(){



if(isRecording){

stopRecording();

}




if(socket){


socket.send(
JSON.stringify({

type:"leave"

})
);


socket.close();

socket=null;


}




if(pc){


pc.close();

pc=null;


}





if(localStream){


localStream
.getTracks()
.forEach(
track=>track.stop()
);



localStream=null;


}




localVideo.srcObject=null;

remoteVideo.srcObject=null;



callOverlay.style.display =
"none";



currentRoom=null;

currentRecipientForCall=null;



}









/* =====================================================
   BUTTON EVENTS
===================================================== */


const phoneBtn =
document.querySelectorAll(
".chat-actions button"
)[0];



const videoBtn =
document.querySelectorAll(
".chat-actions button"
)[1];



const screenShareHeaderBtn =
document.getElementById(
"screenShareHeaderBtn"
);



const audioCallBtn =
document.getElementById(
"audioCallBtn"
);



const videoCallBtn =
document.getElementById(
"videoCallBtn"
);



const shareScreenBtn =
document.getElementById(
"shareScreenBtn"
);





if(phoneBtn){

phoneBtn.onclick=()=>{

startCall({
video:false
});

};

}





if(videoBtn){

videoBtn.onclick=()=>{

startCall({
video:true
});

};

}





if(audioCallBtn){

audioCallBtn.onclick=()=>{

startCall({
video:false
});

};

}





if(videoCallBtn){

videoCallBtn.onclick=()=>{

startCall({
video:true
});

};

}





if(screenShareHeaderBtn){

screenShareHeaderBtn.onclick =
startScreenShareCall;

}



if(shareScreenBtn){

shareScreenBtn.onclick =
startScreenShareCall;

}





endCallBtn.onclick=()=>{


endCall();


};







muteBtn.onclick=()=>{


if(!localStream)
return;



isMuted=!isMuted;



localStream
.getAudioTracks()
.forEach(
track=>{

track.enabled=!isMuted;

});



muteBtn.innerHTML =
isMuted
?
'<i class="fa-solid fa-microphone-slash"></i>'
:
'<i class="fa-solid fa-microphone"></i>';



};








toggleCameraBtn.onclick=()=>{


if(!localStream)
return;



isCameraOff=!isCameraOff;



localStream
.getVideoTracks()
.forEach(
track=>{

track.enabled=!isCameraOff;

});



toggleCameraBtn.innerHTML =
isCameraOff
?
'<i class="fa-solid fa-video-slash"></i>'
:
'<i class="fa-solid fa-video"></i>';



};







recordCallBtn.onclick=()=>{


if(isRecording){

stopRecording();

}
else{

startRecording();

}


};




const stopScreenShareBtn =
document.getElementById(
"stopScreenShareBtn"
);



if(stopScreenShareBtn){


stopScreenShareBtn.onclick=()=>{

endCall();

};


}



});