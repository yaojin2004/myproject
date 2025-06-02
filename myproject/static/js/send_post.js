document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('.post_box');
  const titleInput = document.getElementById('post_title');
  const contentInput = document.getElementById('post_content');
  const fileLinkInput = document.getElementById('file_link');
  const priceInput = document.getElementById('price');
  const sendButton = document.querySelector('.send');

  // 移除错误状态
  function removeError(element) {
    element.classList.remove('error');
    const errorMessage = element.parentElement.querySelector('.error-message');
    if (errorMessage) {
      errorMessage.remove();
    }
  }

  // 添加错误状态
  function addError(element, message) {
    element.classList.add('error');
    const errorMessage = document.createElement('div');
    errorMessage.className = 'error-message';
    errorMessage.textContent = message;
    element.parentElement.appendChild(errorMessage);
  }

  // 验证价格输入
  function validatePrice(price) {
    const priceRegex = /^\d+(\.\d{0,2})?$/;
    return priceRegex.test(price) && parseFloat(price) >= 0;
  }

  // 验证URL
  function validateURL(url) {
    if (!url) return true; // 允许为空
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  // 输入框焦点事件
  [titleInput, contentInput, fileLinkInput, priceInput].forEach(input => {
    input.addEventListener('focus', () => removeError(input));
    input.addEventListener('input', () => removeError(input));
  });

  // 价格输入限制
  priceInput.addEventListener('input', function (e) {
    let value = e.target.value;
    // 只允许数字和小数点
    value = value.replace(/[^\d.]/g, '');
    // 确保只有一个小数点
    const parts = value.split('.');
    if (parts.length > 2) {
      value = parts[0] + '.' + parts.slice(1).join('');
    }
    // 限制小数位数
    if (parts.length === 2 && parts[1].length > 2) {
      value = parts[0] + '.' + parts[1].slice(0, 2);
    }
    e.target.value = value;
  });

  // 表单提交处理
  sendButton.addEventListener('click', function (e) {
    e.preventDefault();
    let isValid = true;

    // 验证标题
    if (!titleInput.value.trim()) {
      addError(titleInput, '请输入标题');
      isValid = false;
    }

    // 验证正文
    if (!contentInput.value.trim()) {
      addError(contentInput, '请输入正文内容');
      isValid = false;
    }

    // 验证文件链接
    if (fileLinkInput.value && !validateURL(fileLinkInput.value)) {
      addError(fileLinkInput, '请输入有效的URL地址');
      isValid = false;
    }

    // 验证价格
    if (!validatePrice(priceInput.value)) {
      addError(priceInput, '请输入有效的价格');
      isValid = false;
    }

    if (isValid) {
      // TODO: 在这里添加表单提交逻辑
      console.log('表单验证通过，准备提交');
      // form.submit();
    }
  });
}); 