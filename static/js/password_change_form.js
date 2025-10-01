(function(){
    const pwd = document.getElementById('id_new_password1');
    const bar = document.getElementById('pwd-bar');
    const text = document.getElementById('pwd-text');
    const submit = document.getElementById('submit-btn');
    if (!pwd || typeof zxcvbn === 'undefined') return;
    function update() {
        const val = pwd.value || '';
        if (!val) {
          bar.style.width = '0%';
          bar.className = '';
          text.textContent = '';
          submit && (submit.disabled = true);
          return;
        }
        const res = zxcvbn(val);
        const score = res.score; // 0..4
        const pct = (score / 4) * 100;
        bar.style.width = pct + '%';
        bar.className = '';
        submit && (submit.disabled = false);

        if (score <= 1) { bar.classList.add('very-weak'); text.textContent = 'Very weak — try a longer password with different characters.'; submit && (submit.disabled = true); }
        else if (score === 2) { bar.classList.add('weak'); text.textContent = 'Weak — consider adding more length and symbols.'; submit && (submit.disabled = true); }
        else if (score === 3) { bar.classList.add('medium'); text.textContent = 'Good — reasonably strong.'; }
        else if (score === 4) { bar.classList.add('strong'); text.textContent = 'Strong — great!'; }

        if (res.feedback && res.feedback.warning) {
          text.textContent += (text.textContent ? ' — ' : '') + res.feedback.warning;
        }
  }

  pwd.addEventListener('input', update);
  update();
})();