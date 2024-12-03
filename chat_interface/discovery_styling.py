/* Discovery Mode Container */
.discovery-container {
    background: linear-gradient(135deg, #1e2430 0%, #2d3748 100%);
    border-radius: 12px;
    padding: 20px;
    margin: 1rem 0;
    color: white;
}

/* Category Sections */
.category-section {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.category-section:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
}

.category-title {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    margin-bottom: 16px !important;
    color: rgba(255, 255, 255, 0.95) !important;
    padding-left: 8px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 8px !important;
}

/* Category Buttons */
.category-button {
    background: rgba(255, 255, 255, 0.12) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    padding: 16px 24px !important;
    margin: 8px !important;
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
    height: auto !important;
    text-align: left !important;
    line-height: 1.4 !important;
    min-height: 80px !important;
    display: flex !important;
    align-items: center !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

.category-button:hover {
    background: rgba(255, 255, 255, 0.18) !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
}

/* Path Visualization */
.path-container {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 12px;
    margin: 12px 0;
    color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.path-step {
    display: inline-block;
    padding: 4px 12px;
    margin: 0 4px;
    background: rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.9);
}

.path-arrow {
    color: rgba(255, 255, 255, 0.5);
    margin: 0 8px;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.category-section {
    animation: fadeIn 0.3s ease-out;
}

/* Light Mode Support */
@media (prefers-color-scheme: light) {
    .discovery-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2d3748;
    }
    
    .category-section {
        background: white;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .category-section:hover {
        background: #f8f9fa;
    }
    
    .category-title {
        color: #2d3748 !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .category-button {
        background: #f8f9fa !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        color: #2d3748 !important;
    }
    
    .category-button:hover {
        background: white !important;
        border-color: rgba(0, 0, 0, 0.15) !important;
    }
    
    .path-container {
        background: white;
        color: #2d3748;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .path-step {
        background: #f8f9fa;
        color: #2d3748;
    }
    
    .path-arrow {
        color: #718096;
    }
}