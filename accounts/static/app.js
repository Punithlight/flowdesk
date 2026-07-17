(function () {
  const LEGACY_STORAGE_KEY = 'flowdesk_users_v1';
  const STORAGE_KEY_PREFIX = 'flowdesk_users_by_role_';
  const SESSION_KEY = 'flowdesk_current_user';
  const ADMIN_EMAIL = 'admin@flowdesk.com';
  const ADMIN_PASSWORD = 'admin123';
  const ROLES = ['admin', 'manager', 'hr', 'technical team', 'team lead', 'employee'];

  const PASSWORD_RULES = {
    admin: {
      description: 'Admin passwords require 8+ characters, uppercase, lowercase, number, and special character.',
      validate(password) {
        return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/.test(password);
      }
    },
    manager: {
      description: 'Manager passwords require 8+ characters, uppercase, lowercase, and a number.',
      validate(password) {
        return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(password);
      }
    },
    hr: {
      description: 'HR passwords require 7+ characters with letters and numbers.',
      validate(password) {
        return /^(?=.*[a-zA-Z])(?=.*\d).{7,}$/.test(password);
      }
    },
    'technical team': {
      description: 'Technical Team passwords require 7+ characters with letters and numbers.',
      validate(password) {
        return /^(?=.*[a-zA-Z])(?=.*\d).{7,}$/.test(password);
      }
    },
    'team lead': {
      description: 'Team Lead passwords require 6+ characters.',
      validate(password) {
        return /^.{6,}$/.test(password);
      }
    },
    employee: {
      description: 'Employee passwords require 6+ characters.',
      validate(password) {
        return /^.{6,}$/.test(password);
      }
    }
  };

  function getRoleStorageKey(role) {
    return `${STORAGE_KEY_PREFIX}${String(role).toLowerCase().replace(/\s+/g, '_')}`;
  }

  function getUsersByRole(role) {
    if (!role) {
      return [];
    }
    try {
      return JSON.parse(localStorage.getItem(getRoleStorageKey(role))) || [];
    } catch (error) {
      return [];
    }
  }

  function saveUsersByRole(role, users) {
    localStorage.setItem(getRoleStorageKey(role), JSON.stringify(users));
  }

  function saveUsers(users) {
    localStorage.setItem(LEGACY_STORAGE_KEY, JSON.stringify(users));
  }

  function migrateLegacyStorage() {
    const legacy = localStorage.getItem(LEGACY_STORAGE_KEY);
    if (!legacy) {
      return;
    }

    let users;
    try {
      users = JSON.parse(legacy);
    } catch (error) {
      return;
    }

    if (!Array.isArray(users)) {
      return;
    }

    users.forEach((user) => {
      const role = ROLES.includes(user.role) ? user.role : 'employee';
      const existingUsers = getUsersByRole(role);
      if (!existingUsers.some((item) => item.email.toLowerCase() === user.email.toLowerCase())) {
        existingUsers.push({ ...user, role });
        saveUsersByRole(role, existingUsers);
      }
    });

    localStorage.removeItem(LEGACY_STORAGE_KEY);
  }

  function ensureDefaultAdmin() {
    migrateLegacyStorage();
    const adminUsers = getUsersByRole('admin');
    if (!adminUsers.some((user) => user.email.toLowerCase() === ADMIN_EMAIL)) {
      adminUsers.unshift({
        id: 1001,
        fullName: 'Admin User',
        email: ADMIN_EMAIL,
        password: ADMIN_PASSWORD,
        role: 'admin'
      });
      saveUsersByRole('admin', adminUsers);
    }
    return adminUsers;
  }

  function getAllUsers() {
    ensureDefaultAdmin();
    return ROLES.flatMap((role) => getUsersByRole(role));
  }

  function findUserByEmail(email) {
    const normalizedEmail = email.toLowerCase();
    return getAllUsers().find((user) => user.email.toLowerCase() === normalizedEmail) || null;
  }

  function loginUser(email, password, role) {
    if (!role) {
      return null;
    }
    const users = getUsersByRole(role);
    const user = users.find((item) => item.email.toLowerCase() === email.toLowerCase());
    return user && user.password === password ? user : null;
  }

  function getPasswordRuleText(role) {
    return PASSWORD_RULES[role]?.description || 'Password must be at least 6 characters.';
  }

  function isPasswordValidForRole(password, role) {
    if (!role || typeof password !== 'string') {
      return false;
    }
    return PASSWORD_RULES[role]?.validate(password) ?? /^.{6,}$/.test(password);
  }

  function createUser(fullName, email, password, role) {
    const normalizedEmail = email.toLowerCase();

    if (!fullName || !normalizedEmail || !password || !role) {
      throw new Error('Please provide full name, email, password, and role.');
    }

    if (!ROLES.includes(role)) {
      throw new Error('Please choose a valid designation.');
    }

    if (!isPasswordValidForRole(password, role)) {
      throw new Error(`Password does not meet requirements for ${role}. ${getPasswordRuleText(role)}`);
    }

    const users = getAllUsers();
    if (users.some((user) => user.email.toLowerCase() === normalizedEmail)) {
      throw new Error('A user with this email already exists.');
    }

    const newUser = {
      id: Date.now(),
      fullName,
      email: normalizedEmail,
      password,
      role
    };

    const roleUsers = getUsersByRole(role);
    roleUsers.push(newUser);
    saveUsersByRole(role, roleUsers);
    return newUser;
  }

  function resetPassword(email, newPassword) {
    const normalizedEmail = email.toLowerCase();
    const user = findUserByEmail(normalizedEmail);
    if (!user) {
      return null;
    }

    if (!isPasswordValidForRole(newPassword, user.role)) {
      return null;
    }

    const roleUsers = getUsersByRole(user.role);
    const savedUser = roleUsers.find((item) => item.email.toLowerCase() === normalizedEmail);
    if (!savedUser) {
      return null;
    }

    savedUser.password = newPassword;
    saveUsersByRole(user.role, roleUsers);
    return savedUser;
  }

  function setCurrentUser(user) {
    if (user) {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(user));
    } else {
      sessionStorage.removeItem(SESSION_KEY);
    }
  }

  function getCurrentUser() {
    try {
      return JSON.parse(sessionStorage.getItem(SESSION_KEY));
    } catch (error) {
      return null;
    }
  }

  function isAdminCredentials(email, password) {
    ensureDefaultAdmin();
    const users = getUsersByRole('admin');
    const adminUser = users.find((user) => user.email.toLowerCase() === ADMIN_EMAIL);
    if (!adminUser) {
      return false;
    }
    return adminUser.email.toLowerCase() === email.toLowerCase() && adminUser.password === password;
  }

  window.FlowDeskApp = {
    getUsers: getAllUsers,
    saveUsers,
    ensureDefaultAdmin,
    createUser,
    findUserByEmail,
    loginUser,
    resetPassword,
    setCurrentUser,
    getCurrentUser,
    getAllUsers,
    isAdminCredentials,
    isPasswordValidForRole,
    getPasswordRuleText,
    getUsersByRole
  };
})();
