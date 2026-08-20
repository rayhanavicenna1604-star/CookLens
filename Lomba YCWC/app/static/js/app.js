const fileInput = document.querySelector('#fileInput');
const cameraInput = document.querySelector('#cameraInput');
const preview = document.querySelector('#preview');
const previewWrap = document.querySelector('#previewWrap');
let ingredients = [];

document.querySelectorAll('.upload-actions label').forEach(label => {
  if (label.firstChild?.nodeType === Node.TEXT_NODE) {
    label.firstChild.textContent = label.firstChild.textContent.replace(/[📷📁]/gu, '').replace(/\s+/g, ' ').trim() + ' ';
  }
});

[fileInput, cameraInput].forEach(input => input?.addEventListener('change', () => {
  const file = input.files[0];
  if (!file) return;
  preview.src = URL.createObjectURL(file);
  previewWrap.classList.remove('hidden');
  analyze(file);
}));
document.querySelector('#changePhoto')?.addEventListener('click', () => fileInput.click());

async function analyze(file) {
  document.querySelector('#emptyState').classList.add('hidden');
  document.querySelector('#loadingState').classList.remove('hidden');
  const body = new FormData(); body.append('file', file);
  try {
    const response = await fetch('/api/analyze', { method: 'POST', body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analysis failed');
    ingredients = data.ingredients;
    renderIngredients();
    document.querySelector('#resultMessage').textContent = data.message;
    document.querySelector('#safetyNote').textContent = 'Food safety note: ' + data.safety_note;
    document.querySelector('#loadingState').classList.add('hidden');
    document.querySelector('#resultState').classList.remove('hidden');
    if (ingredients.some(item => item.confirmed)) loadRecommendations();
  } catch (error) { document.querySelector('#loadingState').innerHTML = `<h2>We hit a snag.</h2><p>${error.message}</p>`; }
}
function renderIngredients() {
  document.querySelector('#ingredientList').innerHTML = ingredients.length ? ingredients.map((item, index) => `<div class="ingredient-row ${item.confirmed ? '' : 'needs-confirmation'}"><span class="ingredient-dot">${item.confirmed ? 'Confirmed' : 'Check'}</span><strong>${item.name}</strong><span class="confidence">${Math.round(item.confidence * 100)}%</span><span>${item.condition}</span><span>${item.quantity}</span>${!item.confirmed ? `<button class="confirm-button" data-index="${index}">Confirm</button>` : ''}<button class="remove-button" data-index="${index}" aria-label="Remove ${item.name}">Remove</button></div>`).join('') : '<p class="no-detection">No ingredients were added automatically. Please enter the ingredients visible in your photo below.</p>';
  document.querySelectorAll('.confirm-button').forEach(button => button.onclick = () => { ingredients[button.dataset.index].confirmed = true; renderIngredients(); loadRecommendations(); });
  document.querySelectorAll('.remove-button').forEach(button => button.onclick = () => { ingredients.splice(button.dataset.index, 1); renderIngredients(); });
}
document.querySelector('#addIngredient')?.addEventListener('click', () => { const input = document.querySelector('#manualIngredient'); if (input.value.trim()) { ingredients.push({name: input.value.trim(), confidence: 1, condition: 'unknown', quantity: 'unknown', confirmed: true}); input.value = ''; renderIngredients(); loadRecommendations(); } });
document.querySelector('#manualIngredient')?.addEventListener('keydown', event => { if (event.key === 'Enter') { event.preventDefault(); document.querySelector('#addIngredient').click(); } });
document.querySelector('#addFoodList')?.addEventListener('click', () => { const input = document.querySelector('#foodList'); const names = input.value.split(/[\n,]+/).map(value => value.trim()).filter(Boolean); names.forEach(name => { if (!ingredients.some(item => item.name.toLowerCase() === name.toLowerCase())) ingredients.push({name, confidence: 1, condition: 'unknown', quantity: 'unknown', confirmed: true}); }); input.value = ''; renderIngredients(); loadRecommendations(); });
document.querySelectorAll('[data-quick-ingredient]').forEach(button => button.addEventListener('click', () => { const name = button.dataset.quickIngredient; if (!ingredients.some(item => item.name.toLowerCase() === name.toLowerCase())) { ingredients.push({name, confidence: 1, condition: 'unknown', quantity: 'unknown', confirmed: true}); renderIngredients(); loadRecommendations(); } button.classList.add('selected'); }));
document.querySelector('#findRecipes')?.addEventListener('click', loadRecommendations);

async function loadRecommendations() {
  const confirmed = ingredients.filter(item => item.confirmed);
  if (!confirmed.length) return;
  const preferences = {taste: document.querySelector('#taste').value || null, diet: document.querySelector('#diet').value || null, max_time: Number(document.querySelector('#maxTime').value) || null};
  const response = await fetch('/api/recipes/recommend', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ingredients: confirmed, preferences, online: true})});
  const data = await response.json();
  localStorage.setItem('foodRescueIngredients', JSON.stringify(confirmed));
  localStorage.setItem('foodRescueRecipes', JSON.stringify(data));
  const panel = document.querySelector('#recommendationResults');
  panel.innerHTML = `<div class="recommendation-heading"><p class="eyebrow">Recommended for your ingredients</p><h3>Here is what you can cook.</h3></div>${data.recipes.map(recipe => `<a class="mini-recipe" href="${recipe.source_url || `/recipes/${recipe.id}`}" ${recipe.source_url ? 'target="_blank" rel="noreferrer"' : ''}><img src="${recipe.image_url}" alt="${recipe.name}"><span><strong>${recipe.name}</strong><small>${recipe.compatibility}% match · ~Rp ${recipe.estimated_additional_cost.toLocaleString('id-ID')} extra</small></span></a>`).join('')}`;
  panel.classList.remove('hidden');
}
