package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "contrats")
public class Contrat {
    @Id
    private UUID id;

    @Column(nullable = false, unique = true)
    private String numeroContrat;

    @Column(nullable = false)
    private String raisonSociale;

    private String nomPayeur;
    private String nif;
    private String adresse;
    private String emailContact;

    private LocalDate dateDebut;
    private LocalDate dateFin;

    @ManyToOne(optional = false)
    @JoinColumn(name = "categorie_client_id", nullable = false)
    private CategorieClient categorieClient; // CategorieClient 1 -> 0..* Contrat

    @ManyToOne
    @JoinColumn(name = "payeur_id")
    private Payeur payeur; // Payeur 0..1 -> 0..* Contrat

    @ManyToOne
    @JoinColumn(name = "commercial_id")
    private Commercial commercial; // Commercial 0..1 -> 0..* Contrat

    @ManyToOne
    @JoinColumn(name = "type_facture_id")
    private TypeFacture typeFacture; // TypeFacture 0..1 -> 0..* Contrat

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "contrat", cascade = CascadeType.ALL)
    private List<Line> lignes = new ArrayList<>(); // Contrat 1 -> 0..* Line

    @OneToMany(mappedBy = "contrat")
    private List<Invoice> factures = new ArrayList<>(); // Contrat 1 -> 0..* Invoice
}
