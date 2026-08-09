package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "types_facture")
public class TypeFacture {
    @Id
    private UUID id;

    @Column(nullable = false, unique = true)
    private String code;

    @Column(nullable = false)
    private String libelle;

    private String description;

    @OneToMany(mappedBy = "typeFacture")
    private List<Invoice> factures = new ArrayList<>(); // TypeFacture 1 -> 0..* Invoice

    @OneToMany(mappedBy = "typeFacture")
    private List<Contrat> contrats = new ArrayList<>(); // TypeFacture 1 -> 0..* Contrat
}
