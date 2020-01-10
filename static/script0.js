document.addEventListener('DOMContentLoaded',()=>{

  document.querySelector("#create").disabled=true;
  document.querySelector("#create_room").oninput=function(){
    if(document.querySelector("#create_room").value.length>0)
    {
      document.querySelector("#create").disabled=false;
      const request=new XMLHttpRequest();
      request.open('POST','/groupname');
      request.onload=()=>{
        data=JSON.parse(request.responseText);
        if(data.success)
        {
          document.querySelector('#create').value="Join";
        }
        else{
          document.querySelector('#create').value="Create";
        }
      };
      const f=new FormData();
      f.append('room',document.querySelector("#create_room").value);
      request.send(f);
    }
    else {
      document.querySelector("#create").disabled=true;
      document.querySelector('#create').value="Create";
    }



  };


  document.querySelector('.grid-item4').hidden=true;
  document.querySelector('#btn-profile').onclick=()=>{
    document.querySelector('#mymodal2').style.display="block";
  };
  document.querySelector('#btn-create').onclick=()=>{
    document.querySelector('#create_channel').style.display="block";
  }

  document.querySelector('.close').onclick=()=>{
    document.querySelector('#create_channel').style.display="none";
  }

    document.querySelectorAll('.close')[1].onclick=()=>{
      document.querySelector('#mymodal2').style.display="none";
    }
  window.onclick=(evt)=>{
    if(evt.target==document.querySelector('#create_channel') )
    document.querySelector('#create_channel').style.display="none";
    if(evt.target==document.querySelector('#mymodal2'))
    document.querySelector('#mymodal2').style.display="none";

  }

  var socket = io.connect('ws://flackweb.herokuapp.com',{transports: ['websocket']});
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
    document.querySelector('#create').onclick=()=>{

      room=document.querySelector("#create_room").value;
      document.querySelector("#create_room").value="";
      document.querySelector("#create").disabled=true;
      var v=document.querySelector("#channel_list");
      for (var i = 0; i < v.childElementCount; i++) {
          if(v.children[i].innerText==room.trim())
          {
          <!--    document.querySelector(".errormessage").innerHTML="*Chat Room with same name already exists."; -->
            alert("Chat Room with same name already exists.");
            return false;
          }
            }

      socket.emit('join',{'room':room.trim()})
      document.querySelector('#create_channel').style.display="none";
      //document.querySelector('#channel_list').innerHTML="";
      //loadAjax();
      return false;
    };


  });

  socket.on("receive message",(data)=>{

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

  socket.on('join status',(data)=>{
    if(data.display_name==document.querySelector("#username").innerText)
    alert("You joined "+data.room+".")
    else if(data.room==document.querySelector("#room-name").innerText)
    alert(data.display_name+" joined "+data.room+".");
    flag=true
    var v=document.querySelector("#channel_list");
    for (var i = 0; i < v.childElementCount; i++) {
      if(v.children[i].innerText==data.room)
      {
        flag=false;
        break;
      }
    }
    if(flag){
    const li=document.createElement('li');
    var channel=encodeURIComponent( data.room.trim());
     var l='javascript:void(0)';//`/chat/${channel}`;

    li.innerHTML= `<a href=${l} > ${ data.room }</a> `;
    /***/
    li.onclick = (evt) => {
	document.querySelector('.grid-item1').style.opacity="1";
      document.querySelector("#room-name").innerText = evt.target.text;
      //alert(evt.target.text);
      //document.querySelector('#initial_message').hidden=true;

      document.querySelector('#message_room').innerHTML=" <p style='color:snow;'> Loading</p>";
      //console.log(document.querySelector("#room-name").innerText);
      document.querySelector('.grid-item4').hidden=false;

      const request = new XMLHttpRequest();
      request.open("POST", '/chats');
      request.onload = function () {
        if(request.status==200)
        {
          const datalist = JSON.parse(request.responseText);

          document.querySelector('#message_room').innerHTML="";
          if (datalist.success) {
            for (var i = 0; i < datalist.message.length; i++) {
              const message_body = datalist.message[i].message;
              const message_user = datalist.message[i].user;
              const message_time = datalist.message[i].time;
              const adiv = document.createElement('div');
              var alebel = document.createElement('lebel');
              const ap = document.createElement('p');
              const asmall = document.createElement('small');
              ap.innerHTML = datalist.message[i].message;
              asmall.innerHTML = datalist.message[i].time;
              alebel.className = "user";
              if (document.querySelector("#username").innerHTML == message_user) {
                alebel.innerHTML = "You";
                adiv.className = "user_chat_box";
              }
              else {
                adiv.className = "chat_box";
                alebel.innerHTML = message_user;
              }
              ap.className = "message";
              asmall.className = "time text-muted";
              adiv.append(alebel);
              adiv.append(ap);
              adiv.append(asmall);
              document.querySelector("#message_room").append(adiv);
            }
            document.querySelector("#message_room").scrollTo(0, document.querySelector("#message_room").scrollHeight);

              socket.emit('join',{'room':document.querySelector("#room-name").innerText});
          }

        }
        };
      const fdata = new FormData();
      fdata.append('roomname', document.querySelector("#room-name").innerText);
      request.send(fdata);
      return false;
    };
    /***/
    document.querySelector('#channel_list').append(li);
  }
  });
  socket.on("leave status",(data)=>{

    if(document.querySelector("#username").innerHTML==data.display_name){
    alert(`You Left ${data.room} `);
    document.querySelector('#channel_list').innerHTML="";
    
    document.querySelector('.grid-item1').style.opacity="0";
    document.querySelector('.grid-item3').innerHTML="<p id='initial_message'>Please select a chat to display messages.</p>";
    document.querySelector('.grid-item4').style.hidden=true;
loadAjax();
  }
    else if(data.room==document.querySelector("#room-name").innerText)
     {
      alert(`${data.display_name} left ${data.room}`);
    }

  });


  /*   ***** */
  //document.querySelector('#message_room').style.height='520px';
  document.querySelector("#submit").disabled = true;
  document.querySelector("#submit").hidden = false;
  var textarea = document.querySelector('textarea');

  hiddenDiv = document.createElement('div'),
  content = null;
  hiddenDiv.classList.add('ta');
  hiddenDiv.classList.add('hiddendiv')

  textarea.onkeyup= function (evt) {
    /*i=document.querySelector('#textarea');
    i.parentNode.appendChild(hiddenDiv);
    i.style.resize = 'none';
    i.style.overflow = 'hidden';
    content = i.value;
    hiddenDiv.style.visibility = 'hidden';
    hiddenDiv.style.display = 'block';
    i.style.height = hiddenDiv.offsetHeight + 'px';
    hiddenDiv.style.visibility = 'visible';
    hiddenDiv.style.display = 'none';*/
    inpStr= document.querySelector("#textarea").value
    if (inpStr.replace(/\r\n|\r|\n/g, "").length > 0){
      document.querySelector("#submit").disabled = false;
      document.querySelector("#submit").hidden = false;
    }
    else {
      //document.querySelector("#submit").hidden = true;
      document.querySelector("#submit").disabled = true;
    }
  };

  loadAjax();

  function loadAjax(){
    const request = new XMLHttpRequest();
    request.open("POST", "/channel_list");

    request.onload = function () {
      if(request.status==200)
      {
        const newData = JSON.parse(request.responseText);
        if (newData.success) {
          for (var i = 0; i < newData.channels.length; i++) {
            const li = document.createElement('li');
            //var channel = encodeURIComponent(newData.channels[i].trim());
            var l ='javascript:void(0)';//= `/chat/${channel}`;
            li.innerHTML = `<a href=${l} > ${newData.channels[i]}</a> `;
            li.classList.add('chat_room');
            document.querySelector('#channel_list').append(li);
          }
        }

          document.querySelectorAll('.chat_room').forEach(function (a) {
          //console.log('lkjhgfdddddddfgh');
          a.onclick = (evt) => {
            document.querySelector('.grid-item1').style.opacity="1";
            document.querySelector("#room-name").innerText = evt.target.text;
            //alert(evt.target.text);
            //document.querySelector('#initial_message').hidden=true;

            document.querySelector('#message_room').innerHTML=" <p style='color:snow;'>Loading</p>";
            //console.log(document.querySelector("#room-name").innerText);
            document.querySelector('.grid-item4').hidden=false;

            const request = new XMLHttpRequest();
            request.open("POST", '/chats');
            request.onload = function () {
              if(request.status==200)
              {
                const datalist = JSON.parse(request.responseText);

                document.querySelector('#message_room').innerHTML="";
                if (datalist.success) {
                  for (var i = 0; i < datalist.message.length; i++) {
                    const message_body = datalist.message[i].message;
                    const message_user = datalist.message[i].user;
                    const message_time = datalist.message[i].time;
                    const adiv = document.createElement('div');
                    var alebel = document.createElement('lebel');
                    const ap = document.createElement('p');
                    const asmall = document.createElement('small');
                    ap.innerHTML = datalist.message[i].message;
                    asmall.innerHTML = datalist.message[i].time;
                    alebel.className = "user";
                    if (document.querySelector("#username").innerHTML == message_user) {
                      alebel.innerHTML = "You";
                      adiv.className = "user_chat_box";
                    }
                    else {
                      adiv.className = "chat_box";
                      alebel.innerHTML = message_user;
                    }
                    ap.className = "message";
                    asmall.className = "time text-muted";
                    adiv.append(alebel);
                    adiv.append(ap);
                    adiv.append(asmall);
                    document.querySelector("#message_room").append(adiv);
                  }
                  document.querySelector("#message_room").scrollTo(0, document.querySelector("#message_room").scrollHeight);

                    socket.emit('join',{'room':document.querySelector("#room-name").innerText});
                }

              }
              };
            const fdata = new FormData();
            fdata.append('roomname', document.querySelector("#room-name").innerText);
            request.send(fdata);
            return false;
          };
        });
      }
    };
    request.send();
  }
});
