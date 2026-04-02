USE imobiliaria;

SELECT 
    i.id,
    i.quantidade_suites,
    i.quantidade_quartos,
    i.quantidade_banheiros,
    i.quantidade_vagas,
    i.quantidade_cozinhas,
    i.quantidade_churrasqueira,
    i.quantidade_escritorio,
    i.localizacao,
    i.area_total,
    i.area_construida,
    i.valor,
    m.modalidade,
    f.finalidade,
    t.tipo,
    u.utilizacao,
    i.data_inserido,
    i.data_removido,
    i.link
FROM imoveis i
LEFT JOIN modalidades m ON i.modalidade_id = m.id
LEFT JOIN finalidades f ON i.finalidade_id = f.id
LEFT JOIN tipos t ON i.tipo_id = t.id
LEFT JOIN utilizacao u ON i.utilizacao_id = u.id;