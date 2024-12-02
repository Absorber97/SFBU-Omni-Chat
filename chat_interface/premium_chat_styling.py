/* Premium Chat Base */
.premium-chat-container {
    background: linear-gradient(135deg, #f6f8ff 0%, #f1f4ff 100%);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* Mode Toggle */
.mode-toggle {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding: 0.5rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.mode-button {
    padding: 0.8rem 1.5rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.mode-button.active {
    background: #1a73e8;
    color: white;
}

/* Role Selection */
.role-selector {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.role-button {
    flex: 1;
    padding: 0.8rem;
    border-radius: 8px;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    text-align: center;
    cursor: pointer;
}

.role-button:hover {
    transform: translateY(-2px);
}

.role-button.student {
    background: #e8f5e9;
    color: #2e7d32;
}

.role-button.faculty {
    background: #e3f2fd;
    color: #1565c0;
}

.role-button.staff {
    background: #fff3e0;
    color: #ef6c00;
}

.role-button.visitor {
    background: #f3e5f5;
    color: #7b1fa2;
}

/* Chat Interface */
.chatbot-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    margin: 1rem 0;
}

.message-input {
    margin-top: 1rem;
    border-radius: 8px;
    border: 2px solid #e0e0e0;
    transition: all 0.2s ease;
}

.message-input:focus {
    border-color: #1a73e8;
    box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.2);
}

/* Discovery Mode */
.discovery-container {
    padding: 1.5rem;
    background: white;
    border-radius: 12px;
    margin-top: 1rem;
}

.category-selection {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.content-section {
    margin: 1.5rem 0;
    padding: 1.5rem;
    background: #ffffff;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.accordion-header {
    padding: 1rem;
    background: #f8fafb;
    border-radius: 8px 8px 0 0;
    cursor: pointer;
    font-weight: 500;
}

.accordion-content {
    padding: 1rem;
    background: white;
    border-radius: 0 0 8px 8px;
}

/* Suggestion Chips */
.suggestion-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    margin-top: 1.5rem;
}

.suggestion-chip {
    padding: 0.5rem 1rem;
    border-radius: 16px;
    background: #e8f0fe;
    color: #1a73e8;
    border: 1px solid #1a73e8;
    cursor: pointer;
    transition: all 0.2s ease;
}

.suggestion-chip:hover {
    background: #1a73e8;
    color: white;
}

/* Follow-up Chips */
.followup-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    margin-top: 1rem;
}

.followup-chip {
    padding: 0.4rem 0.8rem;
    border-radius: 12px;
    background: #f8f9fa;
    color: #5f6368;
    border: 1px solid #dadce0;
    cursor: pointer;
    transition: all 0.2s ease;
}

.followup-chip:hover {
    background: #f1f3f4;
    border-color: #5f6368;
}

/* Responsive Design */
@media (max-width: 768px) {
    .category-selection {
        flex-direction: column;
    }
    
    .suggestion-container,
    .followup-container {
        justify-content: center;
    }
    
    .role-selector {
        flex-direction: column;
    }
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.content-section {
    animation: fadeIn 0.3s ease-out;
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
    .premium-chat-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    
    .content-section {
        background: #2d2d2d;
        border: 1px solid #404040;
    }
    
    .suggestion-chip {
        background: #404040;
        border-color: #666;
    }
    
    .followup-chip {
        background: #333;
        border-color: #666;
    }
}