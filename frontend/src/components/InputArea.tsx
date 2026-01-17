import { Send } from 'lucide-react';
import React, { useState, useRef, useEffect } from 'react';

interface InputAreaProps {
    onSend: (prompt: string) => void;
    disabled: boolean;
}

export function InputArea({ onSend, disabled }: InputAreaProps) {
    const [prompt, setPrompt] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        if (!prompt.trim() || disabled) return;
        onSend(prompt);
        setPrompt('');
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setPrompt(e.target.value);
        e.target.style.height = 'auto';
        e.target.style.height = e.target.scrollHeight + 'px';
    };

    return (
        <div className={`input-container ${disabled ? 'disabled' : ''}`}>
            <div className="input-wrapper">
                <div className="input-box">
                    <textarea
                        ref={textareaRef}
                        id="prompt-input"
                        placeholder="Décrivez votre tâche..."
                        rows={1}
                        value={prompt}
                        onChange={handleInput}
                        onKeyDown={handleKeyDown}
                        disabled={disabled}
                    />
                    <button onClick={handleSend} className="send-btn" aria-label="Envoyer" disabled={disabled}>
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
}
