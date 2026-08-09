namespace Moov.Facturation.Utilisateurs
{
    /// <summary>
    /// Enumération des rôles utilisateurs
    /// </summary>
    public enum RoleChoices
    {
        /// <summary>
        /// Administrateur système
        /// </summary>
        SUPER_ADMIN,
        
        /// <summary>
        /// Chef du service facturation
        /// </summary>
        CHEF_FACTURATION,
        
        /// <summary>
        /// Agent de facturation
        /// </summary>
        AGENT_FACTURATION,
        
        /// <summary>
        /// Payeur entreprise
        /// </summary>
        PAYEUR,
        
        /// <summary>
        /// Employé d'entreprise
        /// </summary>
        EMPLOYE
    }
}
