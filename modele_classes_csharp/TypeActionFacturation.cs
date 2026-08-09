namespace Moov.Facturation.Facturation
{
    /// <summary>
    /// Enumération des types d'actions sur les factures
    /// </summary>
    public enum TypeActionFacturation
    {
        /// <summary>
        /// Création d'une facture
        /// </summary>
        CREATION,
        
        /// <summary>
        /// Modification d'une facture
        /// </summary>
        MODIFICATION,
        
        /// <summary>
        /// Validation d'une facture
        /// </summary>
        VALIDATION,
        
        /// <summary>
        /// Publication d'une facture
        /// </summary>
        PUBLICATION,
        
        /// <summary>
        /// Annulation d'une facture
        /// </summary>
        ANNULATION
    }
}
