document.addEventListener('DOMContentLoaded', () => {
    const textareaEle = document.getElementById('textarea');
    textareaEle.style.minHeight = '120px';
    textareaEle.addEventListener('input', () => {
        textareaEle.style.height = 'auto';
        textareaEle.style.height = `${textareaEle.scrollHeight}px`;
    });
});
