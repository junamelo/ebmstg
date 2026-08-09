namespace Moov.Facturation.Utilisateurs
{
    /// <summary>
    /// Enumération des statuts utilisateurs
    /// </summary>
    public enum StatusChoices
    {
        /// <summary>
        /// Utilisateur actif
        /// </summary>
        ACTIF,
        
        /// <summary>
        /// Utilisateur inactif
        /// </summary>
        INACTIF,
        
        /// <summary>
        /// Utilisateur suspendu temporairement
        /// </summary>
        SUSPENDU,
        
        /// <summary>
        /// Utilisateur bloqué définitivement
        /// </summary>
        BLOQUE,
        
        /// <summary>
        /// Utilisateur en attente de validation
        /// </summary>
        EN_ATTENTE
    }
}
