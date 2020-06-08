document.addEventListener("DOMContentLoaded",function(){
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
socket.on('connect', ()=>{
socket.emit('join',{'room':document.querySelector("#room-name").innerText});
document.querySelector("#submit").onclick=()=>{
text=document.querySelector("#textarea").value.replace(/(?:\r\n|\r|\n)/g, '<br>');
document.querySelector("#textarea").value="";
document.querySelector("#submit").disabled=true;
socket.emit("send message",{"message":text, "room": document.querySelector("#room-name").innerText});
return false;
};
document.querySelector('#leave').onclick=()=>{
var room=document.querySelector('#room-name').innerText;
socket.emit('leave',{'room':room });
return false;
};
});
socket.on("receive mesage",(data)=>{
console.log(ghjkl)
const div=document.createElement('div');
const lebel=document.createElement('lebel');
const p=document.createElement('p');
const span=document.createElement('small');
p.innerHTML=data.message;
span.innerHTML=data.time;
lebel.className="lead user";
//lebel.style.color="orange";
if(document.querySelector("#username").innerText==data.user)
{
div.className="user_chat_box";
lebel.innerHTML="You";
}
else{
div.className="chat_box";
lebel.innerHTML=data.user;
}
p.className="message";
span.className="time text-muted";
div.append(lebel);
div.append(p);
div.append(span);
cln=div.getAttribute('class')
document.querySelector("#message_room").append(div);
list=document.querySelectorAll(`.${cln}`)
document.querySelector("#message_room").scrollTo(0, document.querySelector('#message_room').scrollTop+list[list.length-1].offsetHeight+10)
});
});