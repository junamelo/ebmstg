import api from './api'

// ────────────────────────────────────────────────────────────
// Service pour la gestion des utilisateurs (Admin/Chef)
// ────────────────────────────────────────────────────────────

/**
 * Récupérer la liste des utilisateurs
 */
export const getUsers = async (params = {}) => {
  try {
    const response = await api.get('/accounts/users/', { params })
    return response.data
  } catch (error) {
    console.error('Erreur lors de la récupération des utilisateurs:', error)
    throw error
  }
}

/**
 * Récupérer un utilisateur par ID
 */
export const getUserById = async (userId) => {
  try {
    const response = await api.get(`/accounts/users/${userId}/`)
    return response.data
  } catch (error) {
    console.error('Erreur lors de la récupération de l\'utilisateur:', error)
    throw error
  }
}

/**
 * Créer un nouvel utilisateur
 */
export const createUser = async (userData) => {
  try {
    const response = await api.post('/accounts/users/', userData)
    return response.data
  } catch (error) {
    console.error('Erreur lors de la création de l\'utilisateur:', error)
    throw error
  }
}

/**
 * Modifier un utilisateur
 */
export const updateUser = async (userId, userData) => {
  try {
    const response = await api.patch(`/accounts/users/${userId}/`, userData)
    return response.data
  } catch (error) {
    console.error('Erreur lors de la modification de l\'utilisateur:', error)
    throw error
  }
}

/**
 * Supprimer un utilisateur
 */
export const deleteUser = async (userId) => {
  try {
    const response = await api.delete(`/accounts/users/${userId}/`)
    return response.data
  } catch (error) {
    console.error('Erreur lors de la suppression de l\'utilisateur:', error)
    throw error
  }
}

/**
 * Changer le statut d'un utilisateur
 */
export const changeUserStatus = async (userId, statusData) => {
  try {
    const response = await api.post(`/accounts/users/${userId}/change_status/`, statusData)
    return response.data
  } catch (error) {
    console.error('Erreur lors du changement de statut:', error)
    throw error
  }
}

/**
 * Récupérer l'historique des statuts d'un utilisateur
 */
export const getUserStatusHistory = async (userId) => {
  try {
    const response = await api.get(`/accounts/users/${userId}/status_history/`)
    return response.data
  } catch (error) {
    console.error('Erreur lors de la récupération de l\'historique:', error)
    throw error
  }
}

/**
 * Récupérer les permissions d'un utilisateur
 */
export const getUserPermissions = async (userId) => {
  try {
    const response = await api.get(`/accounts/users/${userId}/permissions/`)
    return response.data
  } catch (error) {
    console.error('Erreur lors de la récupération des permissions:', error)
    throw error
  }
}

/**
 * Ajouter ou retirer une permission
 */
export const managePermission = async (userId, permissionData) => {
  try {
    const response = await api.post(`/accounts/users/${userId}/assign_permission/`, permissionData)
    return response.data
  } catch (error) {
    console.error('Erreur lors de la gestion de la permission:', error)
    throw error
  }
}

/**
 * Réinitialiser le mot de passe d'un utilisateur
 */
export const resetUserPassword = async (userId, newPassword) => {
  try {
    const response = await api.post(`/accounts/users/${userId}/reset_password/`, {
      new_password: newPassword
    })
    return response.data
  } catch (error) {
    console.error('Erreur lors de la réinitialisation du mot de passe:', error)
    throw error
  }
}

// ────────────────────────────────────────────────────────────
// Constantes pour les statuts et rôles
// ────────────────────────────────────────────────────────────

export const USER_STATUS = {
  ACTIF: { value: 'ACTIF', label: 'Actif', color: '#10b981', icon: '🟢' },
  INACTIF: { value: 'INACTIF', label: 'Inactif', color: '#f59e0b', icon: '🟡' },
  SUSPENDU: { value: 'SUSPENDU', label: 'Suspendu', color: '#ef4444', icon: '🔴' },
  EN_ATTENTE: { value: 'EN_ATTENTE', label: 'En attente', color: '#6b7280', icon: '⏳' },
  BLOQUE: { value: 'BLOQUE', label: 'Bloqué', color: '#1f2937', icon: '⚫' },
}

export const USER_ROLES = {
  SUPER_ADMIN: { value: 'SUPER_ADMIN', label: 'Super Admin', color: '#dc2626' },
  CHEF_FACTURATION: { value: 'CHEF_FACTURATION', label: 'Chef Facturation', color: '#7c3aed' },
  AGENT_FACTURATION: { value: 'AGENT_FACTURATION', label: 'Agent Facturation', color: '#2563eb' },
  PAYEUR: { value: 'PAYEUR', label: 'Payeur', color: '#e05500' },
  EMPLOYE: { value: 'EMPLOYE', label: 'Employé', color: '#059669' },
}

export const PERMISSIONS_LIST = {
  accounts: {
    label: 'Gestion des comptes',
    permissions: [
      { key: 'accounts.create_admin', label: 'Créer des admins', restricted: true },
      { key: 'accounts.create_chef', label: 'Créer des chefs de service', restricted: true },
      { key: 'accounts.create_agent', label: 'Créer des agents' },
      { key: 'accounts.create_payeur', label: 'Créer des payeurs' },
      { key: 'accounts.view_all', label: 'Voir tous les comptes' },
      { key: 'accounts.edit_all', label: 'Modifier tous les comptes' },
      { key: 'accounts.change_status', label: 'Changer le statut des comptes' },
      { key: 'accounts.reset_password', label: 'Réinitialiser les mots de passe' },
    ]
  },
  billing: {
    label: 'Facturation',
    permissions: [
      { key: 'billing.publish', label: 'Publier des factures' },
      { key: 'billing.cancel', label: 'Annuler des factures' },
      { key: 'billing.regenerate', label: 'Régénérer des factures' },
      { key: 'billing.view_all', label: 'Voir toutes les factures' },
      { key: 'billing.export', label: 'Exporter les factures' },
    ]
  },
  tarifs: {
    label: 'Forfaits et services',
    permissions: [
      { key: 'tarifs.create', label: 'Créer des forfaits' },
      { key: 'tarifs.edit', label: 'Modifier des forfaits' },
      { key: 'tarifs.activate', label: 'Activer/Désactiver des forfaits' },
      { key: 'services.create', label: 'Créer des services' },
      { key: 'services.edit', label: 'Modifier des services' },
      { key: 'services.activate', label: 'Activer/Désactiver des services' },
    ]
  },
  reports: {
    label: 'Rapports',
    permissions: [
      { key: 'reports.view_all', label: 'Voir tous les rapports' },
      { key: 'reports.export', label: 'Exporter des rapports' },
    ]
  },
  system: {
    label: 'Système',
    permissions: [
      { key: 'system.view_logs', label: 'Voir les logs système' },
      { key: 'system.edit_settings', label: 'Modifier les paramètres système', restricted: true },
      { key: 'system.backup', label: 'Gérer les sauvegardes', restricted: true },
    ]
  }
}
