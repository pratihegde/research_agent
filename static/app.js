// Deep Research System - UI Controller
class ResearchApp {
    constructor() {
        this.currentThreadId = null;
        this.isProcessing = false;

        this.elements = {
            input: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            newBtn: document.getElementById('newChatBtn'),
            messages: document.getElementById('messages'),
            wrapper: document.getElementById('messagesWrapper'),
            welcome: document.getElementById('welcomeScreen'),
            threadInfo: document.getElementById('threadInfo'),
            threadId: document.getElementById('currentThreadId')
        };

        this.init();
    }

    init() {
        this.elements.sendBtn.onclick = () => this.handleSend();
        this.elements.newBtn.onclick = () => window.location.reload();

        this.elements.input.onkeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        };

        // Auto-growth for textarea
        this.elements.input.oninput = () => {
            this.elements.input.style.height = 'auto';
            this.elements.input.style.height = this.elements.input.scrollHeight + 'px';
        };
    }

    async handleSend() {
        const query = this.elements.input.value.trim();
        if (!query || this.isProcessing) return;

        this.elements.welcome.style.display = 'none';
        this.addMessage(query, 'user');
        this.elements.input.value = '';
        this.elements.input.style.height = 'auto';

        this.setProcessing(true);
        await this.startStream(query);
    }

    setProcessing(val) {
        this.isProcessing = val;
        this.elements.sendBtn.disabled = val;
        this.elements.input.disabled = val;
        this.elements.sendBtn.style.opacity = val ? '0.5' : '1';
    }

    addMessage(text, role) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;

        const avatar = role === 'user' ? '👤' : '🤖';
        const name = role === 'user' ? 'You' : 'Research AI';

        msgDiv.innerHTML = `
            <div class="avatar ${role}-avatar">${avatar}</div>
            <div class="msg-body">
                <div class="msg-name">${name}</div>
                <div class="msg-content">${this.formatText(text)}</div>
            </div>
        `;

        this.elements.messages.appendChild(msgDiv);
        this.scrollToBottom();
        return msgDiv;
    }

    addStatus(text) {
        this.removeStatus();
        const status = document.createElement('div');
        status.className = 'status-bar';
        status.innerHTML = `
            <div class="status-chip">
                <div class="dot"></div>
                <span>${text}</span>
            </div>
        `;
        this.elements.messages.appendChild(status);
        this.scrollToBottom();
    }

    removeStatus() {
        const existing = document.querySelector('.status-bar');
        if (existing) existing.remove();
    }

    scrollToBottom() {
        this.elements.wrapper.scrollTop = this.elements.wrapper.scrollHeight;
    }

    formatText(text) {
        return text.replace(/\n/g, '<br>');
    }

    async startStream(query) {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query, thread_id: this.currentThreadId })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let aiMessage = null;
            let reportData = '';
            let currentEvent = null;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('event:')) {
                        currentEvent = line.replace('event: ', '').trim();
                        this.handleEvent(currentEvent);
                    } else if (line.startsWith('data:')) {
                        const dataStr = line.replace('data: ', '').trim();
                        if (!dataStr) continue;

                        try {
                            const data = JSON.parse(dataStr);

                            if (currentEvent === 'thread_id' && data.thread_id) {
                                this.currentThreadId = data.thread_id;
                                this.elements.threadId.textContent = data.thread_id.split('-')[0];
                                this.elements.threadInfo.style.display = 'block';
                            }
                            else if (currentEvent === 'message' && data.content) {
                                if (!aiMessage) aiMessage = this.addMessage('', 'assistant');
                                reportData += data.content;
                                aiMessage.querySelector('.msg-content').innerHTML = this.markdownToHtml(reportData);
                                this.scrollToBottom();
                            }
                            else if (currentEvent === 'done') {
                                this.renderFinalReport(data, aiMessage);
                            }
                            else if (currentEvent === 'error') {
                                this.removeStatus();
                                this.addMessage(`❌ ${data.error || 'An error occurred'}`, 'assistant');
                                console.error('Research error:', data);
                            }
                        } catch (e) {
                            console.error('Failed to parse SSE data:', e);
                        }
                    }
                }
            }
        } catch (err) {
            console.error(err);
            this.addMessage(`Connection lost: ${err.message}. Please try again.`, 'assistant');
        } finally {
            this.setProcessing(false);
            this.removeStatus();
        }
    }

    handleEvent(event) {
        if (event === 'planning') this.addStatus('Strategizing...');
        else if (event === 'research_progress') this.addStatus('Researching Sources...');
        else if (event === 'writing') {
            this.addStatus('Synthesizing Report...');
            this.scrollToBottom();
        }
    }

    renderFinalReport(data, aiMessage) {
        const content = aiMessage.querySelector('.msg-content');
        let html = `<div class="report-card">`;

        if (data.executive_summary) {
            html += `<h2>Executive Summary</h2><p>${data.executive_summary}</p>`;
        }

        html += this.markdownToHtml(data.report);

        if (data.key_takeaways) {
            html += `<h2>Key Takeaways</h2><ul>`;
            data.key_takeaways.forEach(k => html += `<li>${k}</li>`);
            html += `</ul>`;
        }

        if (data.citations) {
            html += `<h2 style="margin-top:3rem">Sources</h2>`;
            data.citations.forEach((c, i) => {
                html += `
                    <div style="margin-bottom:1rem; font-size: 0.9rem;">
                        <span style="color:var(--accent-primary); font-weight:bold">${i + 1}.</span> 
                        <a href="${c.url}" target="_blank" style="color:var(--text-main); text-decoration:none; border-bottom:1px solid var(--border-glass)">${c.title}</a>
                    </div>
                `;
            });
        }

        html += `</div>`;
        content.innerHTML = html;
        this.scrollToBottom();
    }

    markdownToHtml(md) {
        return md
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/^\- (.*$)/gim, '<li>$1</li>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');
    }
}

document.addEventListener('DOMContentLoaded', () => new ResearchApp());
