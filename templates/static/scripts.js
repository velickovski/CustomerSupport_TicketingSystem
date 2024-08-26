
        // JavaScript for real-time chat application

        // Connect to the server via Socket.IO
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

        // Attach event listener for the Enter key
        document.getElementById('message').addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent the default form submission behavior
                sendMessage(); // Call the sendMessage function
            }
        });

        // Constants and Variables
        const TTS_BUTTON_CLASS = 'tts-button';  // Class name for the TTS button
        let isTtsEnabled = false;  // Default TTS state
        let currentUtterance = null;  // Variable to store the current utterance

        // Handle TTS Toggle Switch
        document.getElementById('tts-toggle').addEventListener('change', function() {
            isTtsEnabled = this.checked;

            if (!isTtsEnabled && currentUtterance) {
                // Stop TTS if it's currently speaking
                speechSynthesis.cancel();
            }
        });

        // Play Text-to-Speech
        function playTTS(text) {
            if (!isTtsEnabled) return;  // Exit if TTS is disabled

            if (currentUtterance) {
                speechSynthesis.cancel();  // Stop any ongoing TTS
            }

            currentUtterance = new SpeechSynthesisUtterance(text);
            const voices = speechSynthesis.getVoices();
            currentUtterance.voice = voices.find(voice => voice.name.includes('Google UK English Female')) || voices[0];

            speechSynthesis.speak(currentUtterance);
        }

        // Add TTS Button Next to a Message
        function addTTSButton(messageElement, text) {
            // Check if the button already exists
            if (messageElement.querySelector(`.${TTS_BUTTON_CLASS}`)) return;

            // Create TTS button
            const button = document.createElement('button');
            button.className = TTS_BUTTON_CLASS;
            button.innerHTML = '<i class="fas fa-volume-up"></i>';  // Speaker icon
            button.title = 'Read Aloud';

            // Add event listener for button click
            button.addEventListener('click', () => {
                playTTS(text);
            });

            // Append button to message element
            messageElement.appendChild(button);
        }