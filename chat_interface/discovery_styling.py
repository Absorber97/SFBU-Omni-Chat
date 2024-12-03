/* Discovery Mode Container */
.discovery-container {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    padding: 20px;
    margin: 1rem 0;
}

/* Suggestion Chips */
.suggestion-chip {
    background: white !important;
    border: 1px solid #1a73e8 !important;
    border-radius: 20px !important;
    padding: 8px 16px !important;
    margin: 4px !important;
    color: #1a73e8 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
}

.suggestion-chip:hover {
    background: #1a73e8 !important;
    color: white !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
}

/* Category Groups */
.category-group {
    background: white;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.category-title {
    font-size: 1.1rem;
    font-weight: 500;
    margin-bottom: 12px;
    color: #1a73e8;
}

/* Content Display */
.content-section {
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.accordion-header {
    background: #f8f9fa;
    padding: 12px;
    border-radius: 8px 8px 0 0;
    font-weight: 500;
    cursor: pointer;
}

.accordion-content {
    padding: 16px;
}

/* Follow-up Suggestions */
.followup-chip {
    background: #f8f9fa !important;
    border: 1px solid #6c757d !important;
    border-radius: 16px !important;
    padding: 6px 12px !important;
    margin: 4px !important;
    color: #495057 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
}

.followup-chip:hover {
    background: #e9ecef !important;
    transform: translateY(-1px);
}

/* Path Visualization */
.path-container {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 12px;
    margin: 12px 0;
}

.path-step {
    display: inline-block;
    padding: 4px 8px;
    margin: 0 4px;
    background: white;
    border-radius: 4px;
    font-size: 0.9rem;
}

.path-arrow {
    color: #6c757d;
    margin: 0 4px;
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
    .discovery-container {
        background: linear-gradient(135deg, #212529 0%, #343a40 100%);
    }
    
    .suggestion-chip {
        background: #343a40 !important;
        border-color: #1a73e8 !important;
    }
    
    .suggestion-chip:hover {
        background: #1a73e8 !important;
    }
    
    .category-group {
        background: #343a40;
    }
    
    .content-section {
        background: #343a40;
    }
    
    .accordion-header {
        background: #212529;
    }
    
    .followup-chip {
        background: #212529 !important;
        border-color: #495057 !important;
    }
    
    .followup-chip:hover {
        background: #343a40 !important;
    }
    
    .path-container {
        background: #212529;
    }
    
    .path-step {
        background: #343a40;
    }
}