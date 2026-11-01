/* CarbonKit website. Source and license: https://github.com/smakonin/CarbonKit */
(() => {
  const button = document.querySelector('.nav-toggle');
  const navigation = document.querySelector('#site-nav');
  if (!button || !navigation) return;
  document.documentElement.classList.add('js-nav');
  button.hidden = false;
  const close = () => {
    navigation.classList.remove('is-open');
    button.setAttribute('aria-expanded', 'false');
    button.querySelector('span').textContent = '+';
  };
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') !== 'true';
    button.setAttribute('aria-expanded', String(open));
    navigation.classList.toggle('is-open', open);
    button.querySelector('span').textContent = open ? '−' : '+';
  });
  navigation.addEventListener('click', event => {
    if (event.target.closest('a')) close();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
      close();
      button.focus();
    }
  });
})();
