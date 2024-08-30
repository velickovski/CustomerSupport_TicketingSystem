const socket = io();
        let currentMessageId = null;

        // Automatically focus on the input field when the page loads
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('message').focus();
        });
        
        // Handle incoming messages from the server
        socket.on('response', function(data) {
            console.log('Received data:', data);  // Log received data

            const messageContainer = document.getElementById('chat');

            if (data.formatted) {
                const messageToReplace = document.querySelector(`.bot[data-message-id="${data.message_id}"]`);
                if (messageToReplace) {
                    messageToReplace.innerHTML = formatMarkdown(data.message);
                    scrollToBottom();
                    addTTSButton(messageToReplace, data.message);
                }
            } else {
                if (data.message_id !== currentMessageId) {
                    appendMessage('bot', data.message, data.message_id);
                    currentMessageId = data.message_id;
                } else {
                    const messageToUpdate = document.querySelector(`.bot[data-message-id="${data.message_id}"]`);
                    if (messageToUpdate) {
                        messageToUpdate.textContent += data.message;
                    }
                }
            }
        });

        // Append a new message to the chat container
        function appendMessage(sender, message, messageId) {
            const messageContainer = document.getElementById('chat');
            const newMessage = document.createElement('p');
            newMessage.className = sender;
            newMessage.setAttribute('data-message-id', messageId);
            newMessage.textContent = message;
            messageContainer.appendChild(newMessage);
            scrollToBottom();
        }

        // Format text using markdown
        function formatMarkdown(text) {
            const markdownConverter = new showdown.Converter();
            return markdownConverter.makeHtml(text);
        }

        // Scroll to the bottom of the chat container
        function scrollToBottom() {
            const chatContainer = document.getElementById('chat');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Handle sending a message to the server
        function sendMessage() {
            const messageInput = document.getElementById('message');
            const message = messageInput.value.trim();
            if (message) {
                appendMessage('user', message, null);
                socket.emit('message', { message });
                messageInput.value = '';
            }
        }
        



        function openModal(data) {
            document.getElementById('username').value = data.username || '';
            document.getElementById('description').value = data.description || '';
            document.getElementById('id').value = '';
            document.getElementById('product_description').value = data.item || '';
            
            const modal = document.getElementById('ticketModal');
            modal.style.display = 'block';
            modal.classList.add('show');
            modal.classList.remove('hide');
        }

        function closeModal() {
            const modal = document.getElementById('ticketModal');
            modal.classList.add('hide');
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 500); // Wait for the closing animation to finish
        }


        function submitTicket() {
            const username = document.getElementById('username').value;
            const description = document.getElementById('description').value;
            const id = document.getElementById('id').value;
            const product_description = document.getElementById('product_description').value;
            if (username && description && (id || product_description)) {
                socket.emit('ticket_submission', { username: username, description: description, id: id, product_description: product_description });
                closeModal();
            } else {
                alert('Please fill in all fields.');
            }
        }
        socket.on('ticket', function(data) {
            openModal(data);
        });
        // Attach event listener for the Enter key
        document.getElementById('message').addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent the default form submission behavior
                sendMessage(); // Call the sendMessage function
            }
        });

