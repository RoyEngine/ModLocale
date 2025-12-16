package second_in_command.skills.special.christmas

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.skills.Salvaging
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class ChristmasSpirit : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队与打捞作业"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+30%% 勘探废弃空间站等遗迹设施时获得的资源 - 包括蓝图等稀有物品", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+70%% 勘探废弃空间站等遗迹设施时获得的资源 - 不包括蓝图等稀有物品", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+50%% 战后物品打捞量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+20%% 敌舰击沉后武器掉落概率", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+30%% 载货量和燃料容量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+2 当舰队处于 缓速航行* 时的最大宇宙航行速度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)

        tooltip.addPara("这名军官将于 12 月 27 日 后离开 舰队。", 0f, Misc.getGrayColor(), Misc.getHighlightColor(), "27 日", "离开")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        stats!!.cargoMod.modifyPercent(id, 30f)
        stats!!.fuelMod.modifyPercent(id, 30f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_INCLUDES_RARE).modifyFlat("sc_christmas_spirit", 0.3f, "圣诞妖精")
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_NOT_RARE).modifyFlat("sc_christmas_spirit", 0.7f, "圣诞妖精")
        data.fleet.stats.dynamic.getStat(Stats.BATTLE_SALVAGE_MULT_FLEET).modifyFlat("sc_christmas_spirit", 0.5f)
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WEAPON_RECOVERY_MOD).modifyFlat("sc_christmas_spirit", 0.2f)
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WING_RECOVERY_MOD).modifyFlat("sc_christmas_spirit", 0.2f)
        data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).modifyFlat("sc_christmas_spirit", 2f, "Christmas Spirit")

    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_INCLUDES_RARE).modifyFlat("sc_christmas_spirit", 0.3f, "圣诞妖精")
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_NOT_RARE).modifyFlat("sc_christmas_spirit", 0.7f, "圣诞妖精")
        data.fleet.stats.dynamic.getStat(Stats.BATTLE_SALVAGE_MULT_FLEET).modifyFlat("sc_christmas_spirit", 0.5f)
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WEAPON_RECOVERY_MOD).modifyFlat("sc_christmas_spirit", 0.2f)
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WING_RECOVERY_MOD).modifyFlat("sc_christmas_spirit", 0.2f)
        data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).modifyFlat("sc_christmas_spirit", 2f, "Christmas Spirit")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_INCLUDES_RARE).unmodify("sc_christmas_spirit")
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_NOT_RARE).unmodify("sc_christmas_spirit")
        data.fleet.stats.dynamic.getStat(Stats.BATTLE_SALVAGE_MULT_FLEET).unmodify("sc_christmas_spirit")
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WEAPON_RECOVERY_MOD).unmodify("sc_christmas_spirit")
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WING_RECOVERY_MOD).unmodify("sc_christmas_spirit")
        data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).unmodify("sc_christmas_spirit")
    }
}