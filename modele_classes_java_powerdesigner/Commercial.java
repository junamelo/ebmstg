package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "commerciaux")
public class Commercial {
    @Id
    private UUID id;

    @Column(nullable = false)
    private String nom;

    @Column(nullable = false)
    private String prenom;

    @Column(nullable = false, unique = true)
    private String matricule;

    private String telephone;
    private String email;
    private boolean actif;
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "commercial")
    private List<Contrat> contrats = new ArrayList<>(); // Commercial 1 -> 0..* Contrat
}
