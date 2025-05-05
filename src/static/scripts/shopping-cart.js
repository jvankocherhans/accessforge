const searchInput = document.getElementById('userSearch');
const resultsBox = document.getElementById('autocompleteResults');
const selectedUsersList = document.getElementById('selectedUsersList');
const hiddenInputs = document.getElementById('hiddenInputs');
const submitButton = document.getElementById('submitButton'); // Get the submit button
const addedUsernames = new Set();

async function fetchUsers(query) {
  try {
    const response = await fetch(`/users?query=${query}`);
    const users = await response.json();
    return users.filter(user => user.label.toLowerCase().includes(query.toLowerCase()));
  } catch (error) {
    console.error('Error fetching users:', error);
    return [];
  }
}

searchInput.addEventListener('input', async () => {
  const query = searchInput.value;
  resultsBox.innerHTML = '';
  if (!query) {
    resultsBox.style.display = 'none';
    return;
  }

  const matches = await fetchUsers(query);
  matches.forEach(user => {
    if (!addedUsernames.has(user.username)) {
      const div = document.createElement('div');
      div.textContent = user.label;
      div.onclick = () => addUser(user);
      resultsBox.appendChild(div);
    }
  });

  resultsBox.style.display = matches.length > 0 ? 'block' : 'none';
});

function addUser(user) {
  if (addedUsernames.has(user.username)) return;

  addedUsernames.add(user.username);

  const li = document.createElement('li');
  li.textContent = user.label + ' ';

  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.textContent = 'Remove';
  removeBtn.onclick = () => removeUser(user.username, li, hiddenInput);
  li.appendChild(removeBtn);

  selectedUsersList.appendChild(li);

  const hiddenInput = document.createElement('input');
  hiddenInput.type = 'hidden';
  hiddenInput.name = 'usernames';  // Flask-WTF handles FieldList by repeating same name
  hiddenInput.value = user.username;
  hiddenInputs.appendChild(hiddenInput);

  searchInput.value = '';
  resultsBox.innerHTML = '';
  resultsBox.style.display = 'none';

  // Enable the submit button if there's at least one user
  toggleSubmitButton();
}

function removeUser(username, listItem, hiddenInput) {
  addedUsernames.delete(username);
  listItem.remove();
  hiddenInput.remove();

  // Disable the submit button if no users are left
  toggleSubmitButton();
}

function toggleSubmitButton() {
  if (addedUsernames.size > 0) {
    submitButton.disabled = false;
  } else {
    submitButton.disabled = true;
  }
}
