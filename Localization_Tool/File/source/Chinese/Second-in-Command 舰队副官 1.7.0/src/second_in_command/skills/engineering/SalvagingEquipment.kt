package second_in_command.skills.engineering

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class SalvagingEquipment : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+40%% 勘探废弃空间站等遗迹设施时获得的资源 - 不包括蓝图等稀有物品", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+30%% 战后物品打捞量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("-75%% 非战斗行动中船员损失", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.dynamic.getStat(Stats.NON_COMBAT_CREW_LOSS_MULT).modifyMult("sc_salvaging_equipment", 0.25f)
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_NOT_RARE).modifyFlat("sc_salvaging_equipment", 0.4f, "打捞设备")
        data.fleet.stats.dynamic.getStat(Stats.BATTLE_SALVAGE_MULT_FLEET).modifyFlat("sc_salvaging_equipment", 0.3f, "打捞设备")
    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.dynamic.getStat(Stats.NON_COMBAT_CREW_LOSS_MULT).modifyMult("sc_salvaging_equipment", 0.25f)
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_NOT_RARE).modifyFlat("sc_salvaging_equipment", 0.4f, "打捞设备")
        data.fleet.stats.dynamic.getStat(Stats.BATTLE_SALVAGE_MULT_FLEET).modifyFlat("sc_salvaging_equipment", 0.3f, "打捞设备")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.dynamic.getStat(Stats.NON_COMBAT_CREW_LOSS_MULT).unmodify("sc_salvaging_equipment")
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_NOT_RARE).unmodify("sc_salvaging_equipment")
        data.fleet.stats.dynamic.getStat(Stats.BATTLE_SALVAGE_MULT_FLEET).unmodify("sc_salvaging_equipment")
    }

}