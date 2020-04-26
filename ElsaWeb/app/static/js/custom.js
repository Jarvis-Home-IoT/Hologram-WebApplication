function submit_message(message) {
        $.post( "/send_message", {message: message}, handle_response);

        function handle_response(data) {
          // append the bot repsonse to the div


          $('.direct-chat-messages').append(`

            <div class="direct-chat-msg">
                  <div class="direct-chat-info clearfix">
                    <span class="direct-chat-name pull-left">Javis</span>
                    <span class="direct-chat-timestamp pull-right">time</span>
                  </div>
                  <!-- /.direct-chat-info -->
                  <img class="direct-chat-img" src="/static/img/javis.png" alt="Message User Image">
                  <div class="direct-chat-text">
                    ${data.message}
                  </div>
                  <!-- /.direct-chat-text -->
                </div>

          `)

          // remove the loading indicator
          $( "#loading" ).remove();
          $( ".temp" ).remove();
          $('.appendweather').append(`
          <div class = "temp">
                           <div class="small-box-footer">
              ${data.temp[4]}
            </div>

             <div class="icon">
               <img class = "weather_widget" id = "image" src = "/static/img/ws1.png"/>
            </div>

            <div class="inner">
              <h3 >${data.temp[0]}</h3>
              <p>${data.temp[1]}</p>
              <p>${data.temp[2]}</p>
              <p>${data.temp[3]}</p>
            </div>
      <div class="ban-left-grids">
            <div class="ban-left-grid">
               <h5>${data.info[0]}</h5>

               <img class = "weather_widget2" id = "image1" src = "/static/img/" + ${data.img[0]} + ".png" />
                    <img class = "weather_widget2" id = "image11" src = "/static/img/ws1.png"/>
               <p>${data.info[1]}</p>
            </div>
            <div class="ban-left-grid">
               <h5>${data.info[2]}</h5>
               <img class = "weather_widget2"id = "image2" src = "/static/img/ws1.png"/>
                  <img class = "weather_widget2"id = "image22" src = "/static/img/ws1.png"/>
               <p>${data.info[3]}</p>
            </div>
            <div class="ban-left-grid">
               <h5>${data.info[4]}</h5>
               <img class = "weather_widget2" id = "image3" src = "/static/img/ws1.png"/>
                  <img class = "weather_widget2" id = "image33" src = "/static/img/ws1.png"/>
               <p>${data.info[5]}</p>
            </div>
     <div class="ban-left-grid">
               <h5>${data.info[6]}</h5>
               <img class = "weather_widget2" id = "image4" src = "/static/img/ws1.png"/>
                   <img class = "weather_widget2" id = "image44" src = "/static/img/ws1.png"/>
               <p>${data.info[7]}</p>
            </div>
     <div class="ban-left-grid">
               <h5>${data.info[8]}</h5>
               <img class = "weather_widget2" id = "image5" src = "/static/img/ws1.png"/>
      <img class = "weather_widget2" id = "image55" src = "/static/img/ws1.png"/>

<p>${data.info[9]}</p>


              </div>
                <div class="clearfix"></div>
</div></div>
<script>
 image = document.getElementById('image');
   image1 = document.getElementById('image1');
    image11 = document.getElementById('image11');
    image2 = document.getElementById('image2');
    image22 = document.getElementById('image22');
    image3 = document.getElementById('image3');
     image33 = document.getElementById('image33');
     image4 = document.getElementById('image4');
     image44 = document.getElementById('image44');
     image5 = document.getElementById('image5');
     image55 = document.getElementById('image55');

image.src = '/static/img/' +'${data.img[0]}'+'.png' ;
image1.src = '/static/img/' +'${data.img[1]}'+'.png' ;
    image11.src = '/static/img/' +'${data.img[2]}'+'.png' ;
    image2.src = '/static/img/' +'${data.img[3]}'+'.png' ;
    image22.src = '/static/img/' +'${data.img[4]}'+'.png' ;
    image3.src = '/static/img/' +'${data.img[5]}'+'.png' ;
    image33.src = '/static/img/' +'${data.img[6]}'+'.png' ;
    image4.src = '/static/img/' +'${data.img[7]}'+'.png' ;
    image44.src = '/static/img/' +'${data.img[8]}'+'.png' ;
    image5.src = '/static/img/' +'${data.img[9]}'+'.png' ;
    image55.src = '/static/img/' +'${data.img[10]}'+'.png';</script>
            `)
        }
}
$('#target2').on('submit', function(e){

        e.preventDefault();
        const input_message = $('#input_message2').val()
        // return if the user does not enter any text
        if (!input_message) {
          return
        }

          $('.direct-chat-messages').append(`
           <div class="direct-chat-msg right">
                  <div class="direct-chat-info clearfix">
                    <span class="direct-chat-name pull-right">Choi Hyeyeon</span>
                    <span class="direct-chat-timestamp pull-left">time</span>
                  </div>
                  <!-- /.direct-chat-info -->
                  <img class="direct-chat-img" src="/static/img/girl.png" alt="Message User Image"><!-- /.direct-chat-img -->
                  <div class="direct-chat-text">
                  ${input_message}</div>
                  <!-- /.direct-chat-text -->
                </div>
        `)

        // loading
        $('.direct-chat-messages').append(`
       <div class="direct-chat-msg" id = "loading">
                  <div class="direct-chat-info clearfix">
                    <span class="direct-chat-name pull-left">Javis</span>
                    <span class="direct-chat-timestamp pull-right">time</span>
                  </div>
                  <!-- /.direct-chat-info -->
                  <img class="direct-chat-img" src="/static/img/javis.png" alt="Message User Image"><!-- /.direct-chat-img -->
                  <div class="direct-chat-text">
                    ...
                  </div>
                  <!-- /.direct-chat-text -->
                </div>
        `)

        // clear the text input
        $('#input_message2').val('')

        // send the message
        submit_message(input_message)
 });
