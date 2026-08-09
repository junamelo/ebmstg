using System;
using System.Collections.Generic;

namespace Moov.Facturation.Utilisateurs
{
    /// <summary>
    /// Représente un utilisateur du système (Admin, Chef, Agent, Payeur, Employé)
    /// </summary>
    public class User
    {
        // Attributs
        public string Id { get; set; }
        public string Username { get; set; }
        public string Email { get; set; }
        public string Password { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public RoleChoices Role { get; set; }
        public StatusChoices Status { get; set; }
        public string Telephone { get; set; }
        public bool EstActif { get; set; }
        public DateTime DateCreation { get; set; }
        public DateTime DateModification { get; set; }
        
        // Relations
        public User CreatedBy { get; set; }
        public User StatusChangedBy { get; set; }
        public List<StatusHistory> Historique { get; set; }
        public List<User> UsersCreated { get; set; }
        public List<User> UsersStatusChanged { get; set; }
        
        // Constructeur
        public User()
        {
            Historique = new List<StatusHistory>();
            UsersCreated = new List<User>();
            UsersStatusChanged = new List<User>();
        }
        
        // Méthodes métier
        /// <summary>
        /// Vérifie si l'utilisateur a une permission donnée
        /// </summary>
        public bool HasPermission(string permission)
        {
            // Logique de vérification des permissions
            return true;
        }
        
        /// <summary>
        /// Vérifie si l'utilisateur peut gérer un autre utilisateur
        /// </summary>
        public bool CanManageUser(User targetUser)
        {
            // Logique de vérification hiérarchique
            return true;
        }
    }
}
