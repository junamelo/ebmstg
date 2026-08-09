namespace Moov.Facturation.Contrats
{
    /// <summary>
    /// Enumération des statuts de facturation des contrats
    /// </summary>
    public enum StatutFacturation
    {
        /// <summary>
        /// Facturation active
        /// </summary>
        ACTIF,
        
        /// <summary>
        /// Facturation suspendue temporairement
        /// </summary>
        SUSPENDU,
        
        /// <summary>
        /// Facturation close définitivement
        /// </summary>
        CLOS,
        
        /// <summary>
        /// En attente d'activation
        /// </summary>
        EN_ATTENTE
    }
}
