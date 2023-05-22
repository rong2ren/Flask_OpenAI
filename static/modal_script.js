
function scrollDownToBottom() {
    var objDiv = $("#chat_card_body");
    objDiv.scrollTop(objDiv[0].scrollHeight);
  }

  function human_chat(event){
    event.preventDefault();

    var human_message = $('#human_chat_input').val().trim();
    if (human_message !== '') {
      var human_message_div = $('<div>', {
          class: 'd-flex flex-row justify-content-end mb-4',
          html: $('<div>', {
            class: 'p-3 me-3 border human_chat',
            html: $('<p>', {
              class: 'small mb-0',
              text: human_message
            })
          }).add($('<img>', {
            class: 'avatar_img',
            src: '/static/user.png',
            alt: 'human'
          }))
        });
        $('#chat_card_body').append(human_message_div);
        $('#human_chat_input').val("")
        scrollDownToBottom();
        $('#chat_btn').html('<i class="fas fa-circle-notch fa-spin"></i>');
        chat_ajax_call(human_message)
        $('#chat_btn').html('<i class="fa fa-paper-plane"></i>');
    }
  }

  function chat_ajax_call(user_message){
    $.ajax({
      url: '/chat',
      method: 'POST',
      data: {
        userMessage: user_message
      },
      success: function(data) {
        if (data.error) {
          console.error(data.error)             
        } else {
          // add ai response
          var ai_message_div = $('<div>', {
            class: 'd-flex flex-row justify-content-start mb-4',
            html: $($('<img>', {
              class: 'avatar_img',
              src: '/static/ai.png',
              alt: 'human'
            })).add('<div>', {
              class: 'p-3 me-3 border ai_chat',
              html: $('<p>', {
                class: 'small mb-0',
                text: data.ai_response
              })
            })
          });
          $('#chat_card_body').append(ai_message_div);
          scrollDownToBottom();
        }
      },
      error: function(xhr, status, error) {
          // handle error response
          if (xhr.status === 400) {
            console.error('User input is required.');
          } else if (xhr.status === 500) {
            console.error('An error occurred while server processing the request.');
          } else {
            console.error(xhr.status + "Unknown error occurred.");
          }
          console.error(xhr.responseText);
          console.error(status);
          console.error(error);
      }

    });
  }