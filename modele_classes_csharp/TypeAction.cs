namespace Moov.Facturation.Contrats
{
    /// <summary>
    /// Enumération des types d'actions sur les contrats
    /// </summary>
    public enum TypeAction
    {
        /// <summary>
        /// Création d'un contrat
        /// </summary>
        CREATION,
        
        /// <summary>
        /// Modification d'un contrat
        /// </summary>
        MODIFICATION,
        
        /// <summary>
        /// Résiliation d'un contrat
        /// </summary>
        RESILIATION,
        
        /// <summary>
        /// Suspension d'un contrat
        /// </summary>
        SUSPENSION,
        
        /// <summary>
        /// Réactivation d'un contrat
        /// </summary>
        REACTIVATION
    }
}
