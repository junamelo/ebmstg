package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "categories_client")
public class CategorieClient {
    @Id
    private UUID id;

    @Column(nullable = false, unique = true)
    private String code;

    @Column(nullable = false)
    private String libelle;

    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "categorieClient")
    private List<Contrat> contrats = new ArrayList<>(); // CategorieClient 1 -> 0..* Contrat
}
