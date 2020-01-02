document.addEventListener("DOMContentLoaded",function(){


  const request=new XMLHttpRequest();

  request.open("POST", '/chats');
  request.onload=function(){
    const datalist=JSON.parse(request.responseText);
    if(datalist.success)
    {
      for(var i=0;i<datalist.message.length;i++)
      {
        const message_body=datalist.message[i].message;
        const message_user=datalist.message[i].user;
        const message_time=datalist.message[i].time;
        const adiv=document.createElement('div');
        var alebel=document.createElement('lebel');
        const ap=document.createElement('p');
        const asmall=document.createElement('small');

        //alebel.innerHTML=message_user;
        ap.innerHTML=datalist.message[i].message;
        asmall.innerHTML=datalist.message[i].time;
        alebel.className="user";
        //alebel.style.color="#eb346b";

        if(document.querySelector("#username").innerHTML==message_user)
        {
          alebel.innerHTML="You";
        adiv.className="user_chat_box";
        }
        else{
        adiv.className="chat_box";
        alebel.innerHTML=message_user;
        }
        ap.className="message";
        asmall.className="time text-muted";
        adiv.append(alebel);
        adiv.append(ap);
        adiv.append(asmall);


        document.querySelector("#message_room").append(adiv);
        //document.querySelector("#message_room").innerHTML="Hi user ."+datalist.message.length;
      }
    }


  };
  const fdata=new FormData();
  fdata.append('roomname',document.querySelector("#roomname").innerHTML);
  request.send(fdata);




  document.querySelector("#submit").disabled=true;

  document.querySelector("#textarea").onkeyup=function(){
    if(document.querySelector("#textarea").value.length>0)
    document.querySelector("#submit").disabled=false;
    else {
      document.querySelector("#submit").disabled=true;
    }
  };




  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
  socket.on('connect', ()=>{
    socket.emit('join',{'room':document.querySelector("#roomname").innerHTML});


    document.querySelector("#send_chat").onsubmit=()=>{
      text=document.querySelector("#textarea").value.replace(/(?:\r\n|\r|\n)/g, '<br>');
      document.querySelector("#textarea").value="";
      document.querySelector("#submit").disabled=true;
      socket.emit("send message",{"message":text, "room": document.querySelector("#roomname").innerHTML});
      return false;

    };
  });

  socket.on("receive mesage",(data)=>{
    const div=document.createElement('div');
    const lebel=document.createElement('lebel');
    const p=document.createElement('p');
    const span=document.createElement('small');


    p.innerHTML=data.message;
    span.innerHTML=data.time;
    lebel.className="lead user";
    //lebel.style.color="orange";
    if(document.querySelector("#username").innerHTML==data.user)
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

    window.scrollTo(window.scrollX,window.scrollY+list[list.length-1].offsetHeight)


  });



});
